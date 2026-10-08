from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import Barber, StaffReservation

STUDIO_TZ = ZoneInfo("Europe/Warsaw")
BOOKING_HORIZON_DAYS = 60
MIN_NOTICE = timedelta(minutes=30)
SLOT_STEP = timedelta(minutes=15)


def studio_today():
    return timezone.now().astimezone(STUDIO_TZ).date()


def validate_date(day):
    if day < studio_today() or day > studio_today() + timedelta(days=BOOKING_HORIZON_DAYS):
        raise ValidationError({"date": "Choose a date within the next 60 days."})


def local_instant(day, at):
    return datetime.combine(day, at, tzinfo=STUDIO_TZ)


def is_unambiguous(value):
    return value.replace(fold=0).utcoffset() == value.replace(fold=1).utcoffset()


def offers_service(barber, service):
    if not barber.is_active or not service.is_active or not barber.services.filter(pk=service.pk).exists():
        return False
    if service.training_for_id:
        return bool(barber.level == Barber.Level.TRAINEE and barber.supervisor_id and barber.supervisor.is_active and barber.supervisor.level == Barber.Level.SENIOR and barber.supervisor.services.filter(pk=service.training_for_id, is_active=True).exists())
    return barber.level != Barber.Level.TRAINEE


def staff_slots(barber, duration_minutes, day, *, exclude_id=None, now=None):
    if barber.days_off.filter(date=day).exists():
        return []
    shift = barber.working_hours.filter(weekday=day.weekday()).first()
    if not shift:
        return []
    start, closing = local_instant(day, shift.start_time), local_instant(day, shift.end_time)
    # Skip ambiguous/nonexistent DST wall times instead of silently shifting them.
    if not is_unambiguous(start) or not is_unambiguous(closing) or start.utcoffset() != closing.utcoffset():
        return []
    duration = timedelta(minutes=duration_minutes)
    busy = list(StaffReservation.objects.filter(
        barber=barber,
        starts_at__lt=closing, ends_at__gt=start,
    ).exclude(appointment_id=exclude_id).values_list("starts_at", "ends_at"))
    busy += [(local_instant(day, b.start_time), local_instant(day, b.end_time)) for b in barber.breaks.filter(weekday=day.weekday())]
    earliest = (now or timezone.now()) + MIN_NOTICE
    result = []
    cursor = start
    while cursor + duration <= closing:
        end = cursor + duration
        if is_unambiguous(cursor) and is_unambiguous(end) and cursor >= earliest and not any(cursor < right and end > left for left, right in busy):
            result.append(cursor)
        cursor += SLOT_STEP
    return result


def slots_for(barber, service, day, *, exclude_id=None, now=None):
    validate_date(day)
    if not offers_service(barber, service):
        return []
    slots = staff_slots(barber, service.duration_minutes, day, exclude_id=exclude_id, now=now)
    if service.training_for_id:
        supervisor_slots = set(staff_slots(barber.supervisor, service.duration_minutes, day, exclude_id=exclude_id, now=now))
        slots = [slot for slot in slots if slot in supervisor_slots]
    return slots


def validate_start(barber, service, starts_at):
    local = starts_at.astimezone(STUDIO_TZ)
    validate_date(local.date())
    if not offers_service(barber, service):
        raise ValidationError({"barber": "This barber does not offer the selected service."})
    if local not in slots_for(barber, service, local.date()):
        from .services import SlotConflict
        raise SlotConflict()
