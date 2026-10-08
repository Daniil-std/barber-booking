from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, time
from decimal import Decimal
from threading import Barrier
import secrets
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connections, transaction
from django.test import TransactionTestCase
from rest_framework.test import APIClient, APITestCase

from studio.models import Appointment, Barber, Break, DayOff, Service, StaffReservation, WorkingHours
from studio.scheduling import STUDIO_TZ, slots_for
from .test_booking import DAY, NOW, booking_data


def training_catalog():
    cut = Service.objects.create(name="Signature", description="Cut", duration_minutes=45, price="70.00", senior_price="100.00", top_price="140.00")
    training = Service.objects.create(name="Training", description="Senior supervision", duration_minutes=60, price="35.00", training_for=cut)
    senior = Barber.objects.create(name="Sam", role="Senior", initials="S", level=Barber.Level.SENIOR)
    senior.services.add(cut)
    trainee = Barber.objects.create(name="Noah", role="Training", initials="N", level=Barber.Level.TRAINEE, supervisor=senior)
    trainee.services.add(training)
    for person in [senior, trainee]:
        WorkingHours.objects.create(barber=person, weekday=DAY.weekday(), start_time=time(10), end_time=time(19))
    return cut, training, senior, trainee


class TrainingTests(APITestCase):
    def setUp(self):
        self.clock = patch("django.utils.timezone.now", return_value=NOW)
        self.clock.start()
        self.addCleanup(self.clock.stop)
        cache.clear()
        self.cut, self.training, self.senior, self.trainee = training_catalog()
        self.user = get_user_model().objects.create_user("training@example.test", secrets.token_urlsafe(24))
        self.client.force_authenticate(self.user)

    def book(self, training=True, hour=11, minute=0, **overrides):
        data = booking_data(self.training if training else self.cut, self.trainee if training else self.senior, hour, minute)
        data.update(overrides)
        return self.client.post("/api/appointments/", data, format="json")

    def test_all_level_prices_and_snapshot(self):
        for level, expected in [(Barber.Level.JUNIOR, "70.00"), (Barber.Level.SENIOR, "100.00"), (Barber.Level.TOP, "140.00")]:
            self.senior.level = level
            self.senior.save()
            response = self.book(training=False)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data["price"], expected)
            self.assertEqual(response.data["barber_level"], level)
            self.client.post(f"/api/appointments/{response.data['id']}/cancel/")
        self.cut.top_price = "200.00"
        self.cut.save()
        self.assertEqual(str(Appointment.objects.order_by("pk").last().price), "140.00")

    def test_training_is_half_junior_and_reserves_both_staff(self):
        response = self.book()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["price"], "35.00")
        self.assertEqual(response.data["supervisor_name"], "Sam")
        self.assertEqual(response.data["duration_minutes"], 60)
        self.assertEqual(StaffReservation.objects.count(), 2)
        self.assertEqual(self.book(training=False, minute=15).status_code, 409)
        self.assertEqual(self.book(training=False, hour=12).status_code, 201)

    def test_senior_booking_hides_and_rejects_training_slot(self):
        self.assertEqual(self.book(training=False).status_code, 201)
        self.assertNotIn(time(11), [slot.time() for slot in slots_for(self.trainee, self.training, DAY)])
        self.assertEqual(self.book().status_code, 409)

    def test_supervisor_break_day_off_and_shift_are_respected(self):
        Break.objects.create(barber=self.senior, weekday=DAY.weekday(), start_time=time(11), end_time=time(12))
        self.assertEqual(self.book().status_code, 409)
        DayOff.objects.create(barber=self.senior, date=DAY)
        self.assertEqual(slots_for(self.trainee, self.training, DAY), [])
        DayOff.objects.all().delete()
        WorkingHours.objects.filter(barber=self.senior).update(end_time=time(17))
        self.assertEqual(slots_for(self.trainee, self.training, DAY)[-1].time(), time(16))

    def test_cancel_releases_supervisor_in_api_and_admin_updates(self):
        item = self.book().data
        self.client.post(f"/api/appointments/{item['id']}/cancel/")
        self.assertEqual(StaffReservation.objects.count(), 0)
        self.assertEqual(self.book(training=False).status_code, 201)
        Appointment.objects.filter(status="confirmed").update(status="cancelled")
        self.assertEqual(StaffReservation.objects.count(), 0)
        self.assertEqual(self.book().status_code, 201)

    def test_invalid_training_assignments_and_client_overrides(self):
        self.assertEqual(self.book(service=self.cut.pk).status_code, 400)
        self.assertEqual(self.book(barber=self.senior.pk).status_code, 400)
        self.assertEqual(self.book(price="1.00").status_code, 400)
        self.assertEqual(self.book(supervisor=None).status_code, 400)
        self.senior.is_active = False
        self.senior.save()
        self.assertEqual(slots_for(self.trainee, self.training, DAY), [])
        self.assertEqual(self.book().status_code, 400)

    def test_training_discount_tracks_reference_but_existing_price_is_preserved(self):
        first = self.book().data
        self.client.post(f"/api/appointments/{first['id']}/cancel/")
        self.cut.price = Decimal("80.00")
        self.cut.save()
        self.assertEqual(self.book().data["price"], "40.00")
        self.assertEqual(str(Appointment.objects.get(pk=first["id"]).price), "35.00")

    def test_catalog_contains_authoritative_quotes(self):
        catalog = self.client.get("/api/catalog/").data
        training = next(service for service in catalog["services"] if service["id"] == self.training.pk)
        self.assertEqual(training["min_price"], "35.00")
        self.assertEqual(training["prices"], [{"barber_id": self.trainee.pk, "level": "trainee", "price": "35.00"}])
        self.assertTrue(training["is_training"])

    def test_admin_rejects_training_without_active_senior(self):
        self.trainee.supervisor = None
        with self.assertRaises(ValidationError):
            self.trainee.full_clean()
        self.trainee.supervisor = self.senior
        self.senior.level = Barber.Level.TOP
        self.senior.save()
        with self.assertRaises(ValidationError):
            self.trainee.full_clean()

    def test_database_rejects_prices_in_wrong_tier_order(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Service.objects.filter(pk=self.cut.pk).update(senior_price="60.00")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Service.objects.filter(pk=self.cut.pk).update(top_price="90.00")


class SupervisionConcurrencyTests(TransactionTestCase):
    def setUp(self):
        self.cut, self.training, self.senior, self.trainee = training_catalog()
        self.user = get_user_model().objects.create_user("parallel@example.test", secrets.token_urlsafe(24))
        cache.clear()

    def test_simultaneous_training_and_senior_requests_have_one_winner(self):
        barrier = Barrier(2)

        def worker(training):
            try:
                client = APIClient()
                client.force_authenticate(get_user_model().objects.get(pk=self.user.pk))
                data = booking_data(self.training if training else self.cut, self.trainee if training else self.senior)
                barrier.wait(timeout=10)
                return client.post("/api/appointments/", data, format="json").status_code
            finally:
                connections.close_all()

        with patch("django.utils.timezone.now", return_value=NOW), ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(worker, [True, False]))
        self.assertEqual(sorted(results), [201, 409])
        self.assertEqual(Appointment.objects.count(), 1)

    def test_database_blocks_cross_role_concurrent_direct_inserts(self):
        barrier = Barrier(2)

        def worker(training):
            try:
                person = self.trainee if training else self.senior
                item = Appointment(customer_id=self.user.pk, barber=person, service=self.training if training else self.cut,
                    supervisor=self.senior if training else None, starts_at=datetime.combine(DAY, time(11), tzinfo=STUDIO_TZ),
                    contact_name="Test", contact_email="test@example.test", contact_phone="555010123")
                item.snapshot_service()
                barrier.wait(timeout=10)
                try:
                    with transaction.atomic():
                        item.save()
                    return "created"
                except IntegrityError:
                    return "conflict"
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(worker, [True, False]))
        self.assertEqual(sorted(results), ["conflict", "created"])
        self.assertEqual(Appointment.objects.count(), 1)
