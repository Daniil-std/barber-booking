from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, time, timedelta, timezone as dt_timezone
from threading import Barrier
import secrets
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management import call_command
from django.db import IntegrityError, close_old_connections, connections, transaction
from django.test import TransactionTestCase
from rest_framework.test import APIClient, APITestCase

from studio.models import Appointment, Barber, Break, DayOff, Service, WorkingHours
from studio.scheduling import STUDIO_TZ, slots_for

NOW = datetime(2026, 10, 7, 8, tzinfo=dt_timezone.utc)
DAY = date(2026, 10, 12)


def make_catalog():
    cut = Service.objects.create(name="Signature cut", description="Demo cut", duration_minutes=45, price="120.00")
    reset = Service.objects.create(name="Full reset", description="Demo reset", duration_minutes=75, price="180.00")
    barber = Barber.objects.create(name="Alex", role="Barber", bio="Demo profile", initials="A")
    barber.services.add(cut, reset)
    for weekday in range(7):
        WorkingHours.objects.create(barber=barber, weekday=weekday, start_time=time(10), end_time=time(19))
        Break.objects.create(barber=barber, weekday=weekday, start_time=time(13), end_time=time(13, 30))
    return cut, reset, barber


def booking_data(service, barber, hour=11, minute=0):
    return {
        "service": service.pk, "barber": barber.pk,
        "starts_at": datetime.combine(DAY, time(hour, minute), tzinfo=STUDIO_TZ).isoformat(),
        "contact_name": "Demo Customer", "contact_email": "customer@example.test",
        "contact_phone": "+48 555 010 123", "notes": "Demo appointment",
    }


class BookingTests(APITestCase):
    def setUp(self):
        self.clock = patch("django.utils.timezone.now", return_value=NOW)
        self.clock.start()
        self.addCleanup(self.clock.stop)
        cache.clear()
        self.cut, self.reset, self.barber = make_catalog()
        self.user = get_user_model().objects.create_user("customer@example.test", secrets.token_urlsafe(24))
        self.other = get_user_model().objects.create_user("other@example.test", secrets.token_urlsafe(24))
        self.client.force_authenticate(self.user)

    def book(self, selected_service=None, **overrides):
        data = booking_data(selected_service or self.cut, self.barber)
        data.update(overrides)
        return self.client.post("/api/appointments/", data, format="json")

    def test_success_duration_price_and_snapshot(self):
        response = self.book()
        self.assertEqual(response.status_code, 201)
        item = Appointment.objects.get(pk=response.data["id"])
        self.assertEqual(item.ends_at - item.starts_at, timedelta(minutes=45))
        self.assertEqual(item.customer, self.user)
        self.cut.price = "200.00"
        self.cut.duration_minutes = 60
        self.cut.save()
        item.refresh_from_db()
        self.assertEqual(str(item.price), "120.00")
        self.assertEqual(item.duration_minutes, 45)

    def test_same_slot_is_rejected(self):
        self.assertEqual(self.book().status_code, 201)
        self.assertEqual(self.book().status_code, 409)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_different_duration_overlap_and_adjacent_boundary(self):
        self.assertEqual(self.book().status_code, 201)
        before = datetime.combine(DAY, time(10, 30), tzinfo=STUDIO_TZ).isoformat()
        self.assertEqual(self.book(self.reset, starts_at=before).status_code, 409)
        adjacent = datetime.combine(DAY, time(11, 45), tzinfo=STUDIO_TZ).isoformat()
        self.assertEqual(self.book(self.reset, starts_at=adjacent).status_code, 201)

    def test_cancel_is_idempotent_and_releases_slot(self):
        created = self.book().data
        url = f"/api/appointments/{created['id']}/cancel/"
        self.assertEqual(self.client.post(url).data["status"], "cancelled")
        self.assertEqual(self.client.post(url).status_code, 200)
        self.assertEqual(self.book().status_code, 201)

    def test_ownership_and_unknown_fields(self):
        item = self.book().data
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get("/api/appointments/").data, [])
        self.assertEqual(self.client.get(f"/api/appointments/{item['id']}/").status_code, 404)
        self.assertEqual(self.client.post(f"/api/appointments/{item['id']}/cancel/").status_code, 404)
        self.assertEqual(self.book(customer=self.user.pk).status_code, 400)
        self.assertEqual(self.book(status="cancelled").status_code, 400)
        self.assertEqual(self.client.patch(f"/api/appointments/{item['id']}/", {}, format="json").status_code, 405)

    def test_authentication_required(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get("/api/appointments/").status_code, 403)
        self.assertEqual(self.book().status_code, 403)

    def test_invalid_contact_and_datetime(self):
        for override in [
            {"contact_name": "   "}, {"contact_email": "not-an-email"},
            {"contact_phone": "-------"}, {"notes": "x" * 501},
            {"starts_at": "invalid"}, {"starts_at": "2026-10-12T11:00:00"},
            {"service": 99999}, {"starts_at": "2026-09-01T11:00:00+02:00"},
            {"starts_at": "2027-01-01T11:00:00+01:00"},
        ]:
            with self.subTest(override=override):
                self.assertEqual(self.book(**override).status_code, 400)
        self.assertEqual(Appointment.objects.count(), 0)

    def test_break_closing_off_grid_and_notice(self):
        for clock in [time(12, 45), time(13), time(18, 30), time(11, 7)]:
            start = datetime.combine(DAY, clock, tzinfo=STUDIO_TZ).isoformat()
            self.assertEqual(self.book(starts_at=start).status_code, 409)
        self.assertEqual(self.book(starts_at="2026-10-07T10:15:00+02:00").status_code, 409)

    def test_days_off_and_service_assignment(self):
        DayOff.objects.create(barber=self.barber, date=DAY, reason="Demo day off")
        self.assertEqual(slots_for(self.barber, self.cut, DAY), [])
        self.assertEqual(self.book().status_code, 409)
        self.barber.services.remove(self.cut)
        self.assertEqual(self.book().status_code, 400)

    def test_availability_uses_duration_and_warsaw_offsets(self):
        slots = slots_for(self.barber, self.reset, DAY)
        self.assertNotIn(time(12), [s.time() for s in slots])
        self.assertEqual(slots[-1].time(), time(17, 45))
        winter_slots = slots_for(self.barber, self.cut, date(2026, 10, 26))
        self.assertEqual(winter_slots[0].utcoffset(), timedelta(hours=1))
        self.assertEqual(slots[0].utcoffset(), timedelta(hours=2))
        self.assertEqual(self.book(starts_at="2026-10-12T09:00:00Z").status_code, 201)

    def test_dst_transition_hours_are_not_offered(self):
        shift = WorkingHours.objects.get(barber=self.barber, weekday=6)
        shift.start_time, shift.end_time = time(1), time(4)
        shift.save()
        self.assertEqual(slots_for(self.barber, self.cut, date(2026, 10, 25)), [])

    def test_cannot_cancel_started_appointment(self):
        item = self.book().data
        with patch("django.utils.timezone.now", return_value=datetime(2026, 10, 12, 10, tzinfo=dt_timezone.utc)):
            response = self.client.post(f"/api/appointments/{item['id']}/cancel/")
        self.assertEqual(response.status_code, 409)

    def test_seed_is_repeatable_and_has_no_accounts(self):
        call_command("seed_demo", verbosity=0)
        counts = (Service.objects.count(), Barber.objects.count(), WorkingHours.objects.count(), Break.objects.count(), get_user_model().objects.count())
        call_command("seed_demo", verbosity=0)
        self.assertEqual(counts, (Service.objects.count(), Barber.objects.count(), WorkingHours.objects.count(), Break.objects.count(), get_user_model().objects.count()))

    def test_csrf_register_login_logout_and_duplicate_email(self):
        client = APIClient(enforce_csrf_checks=True)
        register = {"first_name": "Taylor", "email": "taylor@example.test", "password": secrets.token_urlsafe(24)}
        self.assertEqual(client.post("/api/auth/register/", register, format="json").status_code, 403)
        token = client.get("/api/auth/session/").data["csrfToken"]
        created = client.post("/api/auth/register/", register, format="json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(created.status_code, 201)
        self.assertNotIn("password", created.data["user"])
        token = created.data["csrfToken"]
        self.assertEqual(client.post("/api/appointments/", booking_data(self.cut, self.barber), format="json").status_code, 403)
        out = client.post("/api/auth/logout/", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(out.status_code, 200)
        token = out.data["csrfToken"]
        duplicate = {**register, "email": "TAYLOR@example.test"}
        self.assertEqual(client.post("/api/auth/register/", duplicate, format="json", HTTP_X_CSRFTOKEN=token).status_code, 400)
        self.assertEqual(client.post("/api/auth/login/", {"email": register["email"], "password": "wrong"}, format="json", HTTP_X_CSRFTOKEN=token).status_code, 400)
        response = client.post("/api/auth/login/", {"email": register["email"], "password": register["password"]}, format="json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(client.get("/api/auth/session/").data["user"]["email"], register["email"])

    def test_weak_password_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        token = client.get("/api/auth/session/").data["csrfToken"]
        response = client.post("/api/auth/register/", {"first_name": "Demo", "email": "demo@example.test", "password": "1234567890"}, format="json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.data["errors"])

    def test_admin_catalog_schedules_and_user_creation(self):
        admin = get_user_model().objects.create_superuser("admin@example.test", secrets.token_urlsafe(24))
        self.client.force_authenticate(None)
        self.client.force_login(admin)
        for page in ["service", "barber", "workinghours", "break", "dayoff", "appointment", "user"]:
            self.assertEqual(self.client.get(f"/admin/studio/{page}/").status_code, 200)
        self.assertEqual(self.client.get("/admin/studio/user/add/").status_code, 200)
        password = secrets.token_urlsafe(24)
        response = self.client.post("/admin/studio/user/add/", {"email": "newadminuser@example.test", "first_name": "Casey", "password1": password, "password2": password})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(get_user_model().objects.filter(email="newadminuser@example.test").exists())


class ConcurrencyTests(TransactionTestCase):
    def setUp(self):
        cache.clear()
        self.cut, self.reset, self.barber = make_catalog()
        self.users = [get_user_model().objects.create_user(f"thread{i}@example.test", secrets.token_urlsafe(24)) for i in range(2)]

    def test_simultaneous_api_requests_have_one_winner(self):
        barrier = Barrier(2)

        def worker(user_id, service_id, minute):
            close_old_connections()
            try:
                client = APIClient()
                client.force_authenticate(get_user_model().objects.get(pk=user_id))
                payload = booking_data(Service.objects.get(pk=service_id), self.barber, 11, minute)
                barrier.wait(timeout=10)
                return client.post("/api/appointments/", payload, format="json").status_code
            finally:
                connections.close_all()

        with patch("django.utils.timezone.now", return_value=NOW), ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(worker, self.users[0].pk, self.cut.pk, 0), pool.submit(worker, self.users[1].pk, self.reset.pk, 15)]
            outcomes = [future.result(timeout=20) for future in futures]
        self.assertEqual(sorted(outcomes), [201, 409])
        self.assertEqual(Appointment.objects.filter(status="confirmed").count(), 1)

    def test_database_constraint_protects_direct_concurrent_writes(self):
        barrier = Barrier(2)

        def worker(user_id):
            close_old_connections()
            try:
                item = Appointment(customer_id=user_id, barber_id=self.barber.pk, service=self.cut,
                    starts_at=datetime.combine(DAY, time(11), tzinfo=STUDIO_TZ),
                    contact_name="Demo", contact_email="demo@example.test", contact_phone="555010123")
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
            results = list(pool.map(worker, [user.pk for user in self.users]))
        self.assertEqual(sorted(results), ["conflict", "created"])
