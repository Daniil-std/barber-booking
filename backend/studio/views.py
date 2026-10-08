from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import Appointment, Barber, Service, User
from .scheduling import slots_for, studio_today
from .serializers import (AppointmentCreateSerializer, AppointmentSerializer, AvailabilitySerializer,
    BarberSerializer, LoginSerializer, RegisterSerializer, ServiceSerializer, UserSerializer)
from .services import cancel_appointment, create_appointment


def session_data(request):
    return {"user": UserSerializer(request.user).data if request.user.is_authenticated else None, "csrfToken": get_token(request)}


@method_decorator(never_cache, name="dispatch")
class SessionView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(session_data(request))


@method_decorator(csrf_protect, name="dispatch")
class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                user = User.objects.create_user(**serializer.validated_data)
        except IntegrityError as exc:
            if getattr(getattr(exc.__cause__, "diag", None), "constraint_name", None) not in {"unique_email_case_insensitive", "studio_user_email_key"}:
                raise
            raise ValidationError({"email": "An account with this email already exists."}) from exc
        login(request, user)
        return Response(session_data(request), status=status.HTTP_201_CREATED)


@method_decorator(csrf_protect, name="dispatch")
class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request, email=serializer.validated_data["email"].lower(), password=serializer.validated_data["password"])
        if user is None:
            raise ValidationError({"detail": "The email or password is incorrect."})
        login(request, user)
        return Response(session_data(request))


@method_decorator(csrf_protect, name="dispatch")
class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response(session_data(request))


class CatalogView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "services": ServiceSerializer(Service.objects.filter(is_active=True).select_related("training_for"), many=True).data,
            "barbers": BarberSerializer(Barber.objects.filter(is_active=True).select_related("supervisor").prefetch_related("services"), many=True).data,
            "timezone": "Europe/Warsaw", "today": studio_today().isoformat(), "booking_horizon_days": 60,
        })


@method_decorator(never_cache, name="dispatch")
class AvailabilityView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        serializer = AvailabilitySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return Response({"slots": [slot.isoformat() for slot in slots_for(data["barber"], data["service"], data["date"])], "timezone": "Europe/Warsaw"})


@method_decorator(never_cache, name="dispatch")
class AppointmentsView(APIView):
    def get(self, request):
        items = Appointment.objects.filter(customer=request.user).select_related("barber")
        return Response(AppointmentSerializer(items, many=True).data)

    def post(self, request):
        serializer = AppointmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = create_appointment(customer=request.user, **serializer.validated_data)
        return Response(AppointmentSerializer(item).data, status=status.HTTP_201_CREATED)


@method_decorator(never_cache, name="dispatch")
class AppointmentDetailView(APIView):
    def get(self, request, pk):
        item = get_object_or_404(Appointment.objects.select_related("barber"), pk=pk, customer=request.user)
        return Response(AppointmentSerializer(item).data)


class CancelAppointmentView(APIView):
    def post(self, request, pk):
        if request.data:
            raise ValidationError({"detail": "This action does not accept additional fields."})
        get_object_or_404(Appointment, pk=pk, customer=request.user)
        return Response(AppointmentSerializer(cancel_appointment(pk, request.user)).data)


def csrf_failure(request, reason=""):
    return JsonResponse({"errors": {"detail": "Your session could not be verified. Refresh the page and try again."}}, status=403)
