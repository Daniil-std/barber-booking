from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateTimeRangeField, RangeOperators
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Lower

WEEKDAYS = [(i, day) for i, day in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])]
phone_validator = RegexValidator(r"^\+?[0-9 ()-]{7,25}$", "Enter a phone number with 7–25 digits, spaces, parentheses or hyphens.")


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("An email address is required.")
        user = self.model(email=email.strip().lower(), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if not extra_fields["is_staff"] or not extra_fields["is_superuser"]:
            raise ValueError("A superuser must have is_staff=True and is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        constraints = [models.UniqueConstraint(Lower("email"), name="unique_email_case_insensitive")]

    def __str__(self):
        return self.email


class Service(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500)
    duration_minutes = models.PositiveSmallIntegerField(validators=[MinValueValidator(15), MaxValueValidator(240)])
    price = models.DecimalField("Junior price", max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])
    senior_price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    top_price = models.DecimalField("Top Barber price", max_digits=7, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveSmallIntegerField(default=0)
    training_for = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="training_services", help_text="Training appointments cost 50% of this service's Junior price and require Senior supervision.")

    class Meta:
        ordering = ["display_order", "id"]
        constraints = [
            models.CheckConstraint(condition=Q(duration_minutes__gte=15, duration_minutes__lte=240, price__gte=0), name="valid_service_duration_price"),
            models.CheckConstraint(condition=(Q(senior_price__isnull=True) | Q(senior_price__gte=F("price"))) & (Q(top_price__isnull=True) | Q(top_price__gte=F("price"))) & (Q(top_price__isnull=True) | Q(senior_price__isnull=True) | Q(top_price__gte=F("senior_price"))), name="valid_service_tier_prices"),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        if self.training_for_id and (self.training_for_id == self.pk or self.training_for.training_for_id):
            raise ValidationError({"training_for": "Choose a regular service as the training reference."})
        if not self.training_for_id:
            if self.senior_price is None or self.top_price is None:
                raise ValidationError("Set prices for Junior, Senior and Top Barber.")
            if not self.price <= self.senior_price <= self.top_price:
                raise ValidationError("Prices must increase from Junior to Senior to Top Barber.")

    @property
    def base_price(self):
        amount = Decimal(self.training_for.price) * Decimal("0.50") if self.training_for_id else Decimal(self.price)
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def price_for(self, barber):
        amount = self.base_price
        if not self.training_for_id:
            tier_price = {"senior": self.senior_price, "top": self.top_price}.get(barber.level)
            if tier_price is not None:
                amount = Decimal(tier_price)
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class Barber(models.Model):
    class Level(models.TextChoices):
        JUNIOR = "junior", "Junior"
        SENIOR = "senior", "Senior"
        TOP = "top", "Top Barber"
        TRAINEE = "trainee", "Barber in training"

    name = models.CharField(max_length=80, unique=True)
    role = models.CharField(max_length=120)
    bio = models.TextField(max_length=500)
    initials = models.CharField(max_length=2)
    services = models.ManyToManyField(Service, related_name="barbers")
    is_active = models.BooleanField(default=True)
    level = models.CharField(max_length=12, choices=Level.choices, default=Level.JUNIOR)
    supervisor = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="trainees", limit_choices_to={"level": "senior", "is_active": True})

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name

    def clean(self):
        if self.level == self.Level.TRAINEE:
            if not self.supervisor_id or self.supervisor_id == self.pk or self.supervisor.level != self.Level.SENIOR or not self.supervisor.is_active:
                raise ValidationError({"supervisor": "Assign an active Senior barber to supervise training appointments."})
        elif self.supervisor_id:
            raise ValidationError({"supervisor": "Only a barber in training can have a supervisor."})


class WorkingHours(models.Model):
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name="working_hours")
    weekday = models.PositiveSmallIntegerField(choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        verbose_name_plural = "working hours"
        ordering = ["barber", "weekday"]
        constraints = [
            models.UniqueConstraint(fields=["barber", "weekday"], name="one_shift_per_day"),
            models.CheckConstraint(condition=Q(start_time__lt=F("end_time"), weekday__lte=6), name="valid_working_hours"),
        ]

    def clean(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError({"end_time": "End time must be after start time. Overnight shifts are not supported."})

    def __str__(self):
        return f"{self.barber} · {self.get_weekday_display()} · {self.start_time:%H:%M}–{self.end_time:%H:%M}"


class Break(models.Model):
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name="breaks")
    weekday = models.PositiveSmallIntegerField(choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ["barber", "weekday", "start_time"]
        constraints = [models.CheckConstraint(condition=Q(start_time__lt=F("end_time"), weekday__lte=6), name="valid_break")]

    def clean(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError({"end_time": "End time must be after start time."})

    def __str__(self):
        return f"{self.barber} · {self.get_weekday_display()} · break"


class DayOff(models.Model):
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name="days_off")
    date = models.DateField()
    reason = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name_plural = "days off"
        ordering = ["-date"]
        constraints = [models.UniqueConstraint(fields=["barber", "date"], name="unique_barber_day_off")]

    def __str__(self):
        return f"{self.barber} · {self.date}"


class Appointment(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    customer = models.ForeignKey(User, on_delete=models.PROTECT, related_name="appointments")
    barber = models.ForeignKey(Barber, on_delete=models.PROTECT, related_name="appointments")
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(editable=False)
    service_name = models.CharField(max_length=100, editable=False)
    price = models.DecimalField(max_digits=7, decimal_places=2, editable=False)
    duration_minutes = models.PositiveSmallIntegerField(editable=False)
    contact_name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=25, validators=[phone_validator])
    notes = models.TextField(max_length=500, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.CONFIRMED)
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True, editable=False)
    barber_level = models.CharField(max_length=12, choices=Barber.Level.choices, default=Barber.Level.JUNIOR, editable=False)
    supervisor = models.ForeignKey(Barber, null=True, blank=True, on_delete=models.PROTECT, related_name="supervised_appointments", editable=False)

    class Meta:
        ordering = ["-starts_at"]
        constraints = [
            models.CheckConstraint(condition=Q(supervisor__isnull=True) | ~Q(barber=F("supervisor")), name="different_training_supervisor"),
            models.CheckConstraint(condition=Q(ends_at__gt=F("starts_at")), name="appointment_positive_duration"),
            models.CheckConstraint(condition=Q(status__in=["confirmed", "cancelled"]), name="appointment_valid_status"),
            ExclusionConstraint(
                name="no_overlapping_confirmed_appointments",
                expressions=[
                    ("barber", RangeOperators.EQUAL),
                    (models.Func("starts_at", "ends_at", models.Value("[)"), function="TSTZRANGE", output_field=DateTimeRangeField()), RangeOperators.OVERLAPS),
                ],
                condition=Q(status="confirmed"),
            ),
        ]
        indexes = [models.Index(fields=["barber", "starts_at"]), models.Index(fields=["customer", "starts_at"])]

    def snapshot_service(self):
        self.service_name = self.service.name
        self.duration_minutes = self.service.duration_minutes
        self.price = self.service.price_for(self.barber)
        self.barber_level = self.barber.level
        self.ends_at = self.starts_at + timedelta(minutes=self.duration_minutes)

    def __str__(self):
        return f"{self.contact_name} · {self.service_name} · {self.starts_at}"


class StaffReservation(models.Model):
    """Confirmed staff occupancy, maintained by a PostgreSQL appointment trigger."""
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="staff_reservations")
    barber = models.ForeignKey(Barber, on_delete=models.PROTECT, related_name="staff_reservations")
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["appointment", "barber"], name="unique_appointment_staff"),
            ExclusionConstraint(name="no_overlapping_staff_reservations", expressions=[
                ("barber", RangeOperators.EQUAL),
                (models.Func("starts_at", "ends_at", models.Value("[)"), function="TSTZRANGE", output_field=DateTimeRangeField()), RangeOperators.OVERLAPS),
            ]),
        ]
