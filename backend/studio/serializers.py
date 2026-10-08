from collections.abc import Mapping
from datetime import datetime

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Appointment, Barber, Service, User, phone_validator
from .scheduling import offers_service


class StrictSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if not isinstance(data, Mapping):
            raise serializers.ValidationError({"detail": "Expected a JSON object."})
        unknown = set(data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError({key: "Unknown field." for key in sorted(unknown)})
        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name"]


class RegisterSerializer(StrictSerializer):
    first_name = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(min_length=10, max_length=128, trim_whitespace=False, write_only=True)

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate(self, attrs):
        try:
            validate_password(attrs["password"], User(email=attrs["email"], first_name=attrs["first_name"]))
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)}) from exc
        return attrs


class LoginSerializer(StrictSerializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(max_length=128, trim_whitespace=False, write_only=True)


class ServiceSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(source="base_price", max_digits=7, decimal_places=2, read_only=True)
    prices = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    is_training = serializers.SerializerMethodField()

    def get_prices(self, service):
        return [{"barber_id": barber.pk, "level": barber.level, "price": str(service.price_for(barber))}
                for barber in service.barbers.filter(is_active=True).select_related("supervisor") if offers_service(barber, service)]

    def get_min_price(self, service):
        from decimal import Decimal
        prices = self.get_prices(service)
        return str(min(Decimal(item["price"]) for item in prices)) if prices else str(service.base_price)

    def get_is_training(self, service):
        return bool(service.training_for_id)

    class Meta:
        model = Service
        fields = ["id", "name", "description", "duration_minutes", "price", "min_price", "prices", "is_training"]


class BarberSerializer(serializers.ModelSerializer):
    level_label = serializers.CharField(source="get_level_display", read_only=True)
    supervisor_name = serializers.CharField(source="supervisor.name", read_only=True, default=None)
    class Meta:
        model = Barber
        fields = ["id", "name", "role", "bio", "initials", "services", "level", "level_label", "supervisor", "supervisor_name"]


class OffsetDateTimeField(serializers.DateTimeField):
    def to_internal_value(self, value):
        if isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    raise serializers.ValidationError("Include a timezone offset in the appointment time.")
            except ValueError:
                pass
        return super().to_internal_value(value)


class AppointmentCreateSerializer(StrictSerializer):
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.filter(is_active=True))
    barber = serializers.PrimaryKeyRelatedField(queryset=Barber.objects.filter(is_active=True))
    starts_at = OffsetDateTimeField()
    contact_name = serializers.CharField(max_length=100)
    contact_email = serializers.EmailField(max_length=254)
    contact_phone = serializers.CharField(max_length=25)
    notes = serializers.CharField(max_length=500, allow_blank=True, default="")

    def validate_contact_phone(self, value):
        try:
            phone_validator(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc
        if not 7 <= sum(c.isdigit() for c in value) <= 15:
            raise serializers.ValidationError("Enter a phone number containing 7–15 digits.")
        return value


class AppointmentSerializer(serializers.ModelSerializer):
    barber_name = serializers.CharField(source="barber.name", read_only=True)
    barber_level_label = serializers.CharField(source="get_barber_level_display", read_only=True)
    supervisor_name = serializers.CharField(source="supervisor.name", read_only=True, default=None)

    class Meta:
        model = Appointment
        fields = ["id", "service", "service_name", "barber", "barber_name", "barber_level", "barber_level_label", "supervisor", "supervisor_name", "starts_at", "ends_at", "duration_minutes", "price", "contact_name", "contact_email", "contact_phone", "notes", "status", "created_at", "cancelled_at"]


class AvailabilitySerializer(StrictSerializer):
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.filter(is_active=True))
    barber = serializers.PrimaryKeyRelatedField(queryset=Barber.objects.filter(is_active=True))
    date = serializers.DateField()
