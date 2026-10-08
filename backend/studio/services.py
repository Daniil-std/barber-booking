from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.exceptions import APIException

from .models import Appointment, Barber, Service
from .scheduling import validate_start


class SlotConflict(APIException):
    status_code = 409
    default_detail = "This time is no longer available. Please choose another slot."
    default_code = "slot_unavailable"


def create_appointment(*, customer, **data):
    try:
        with transaction.atomic():
            # Lock all participating staff in one order. PostgreSQL also enforces
            # occupancy for both the barber and supervisor through a trigger.
            participant_ids = [data["barber"].pk]
            supervisor_id = data["barber"].supervisor_id if data["service"].training_for_id else None
            if supervisor_id:
                participant_ids.append(supervisor_id)
            staff = {person.pk: person for person in Barber.objects.select_for_update().filter(pk__in=participant_ids).order_by("pk")}
            barber = staff[data["barber"].pk]
            service = Service.objects.select_for_update(of=("self",)).select_related("training_for").get(pk=data["service"].pk)
            if service.training_for_id and barber.supervisor_id != supervisor_id:
                raise SlotConflict()
            if supervisor_id:
                barber.supervisor = staff[supervisor_id]
            validate_start(barber, service, data["starts_at"])
            data.update(barber=barber, service=service, supervisor=barber.supervisor if service.training_for_id else None)
            appointment = Appointment(customer=customer, **data)
            appointment.snapshot_service()
            appointment.save()
            return appointment
    except IntegrityError as exc:
        if getattr(getattr(exc.__cause__, "diag", None), "constraint_name", None) in {"no_overlapping_confirmed_appointments", "no_overlapping_staff_reservations"}:
            raise SlotConflict() from exc
        raise


def cancel_appointment(appointment_id, customer):
    with transaction.atomic():
        appointment = Appointment.objects.select_for_update().get(pk=appointment_id, customer=customer)
        if appointment.status == Appointment.Status.CANCELLED:
            return appointment
        if appointment.starts_at <= timezone.now():
            raise SlotConflict("An appointment that has already started cannot be cancelled.")
        appointment.status = Appointment.Status.CANCELLED
        appointment.cancelled_at = timezone.now()
        appointment.save(update_fields=["status", "cancelled_at"])
        return appointment
