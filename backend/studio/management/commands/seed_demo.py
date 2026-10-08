from datetime import time

from django.core.management.base import BaseCommand
from django.db import transaction

from studio.models import Barber, Break, Service, WorkingHours

SERVICES = [
    ("The signature cut", "A considered cut, tailored to you. Consultation, wash, cut and finish.", 45, "70.00", "100.00", "140.00"),
    ("Beard & detail", "Clean lines. A balanced shape. Beard sculpting and a hot towel finish.", 30, "40.00", "60.00", "80.00"),
    ("The full reset", "The complete ritual. Our signature cut with a beard shape and hot towel.", 75, "110.00", "160.00", "220.00"),
    ("The close cut", "Minimal length, maximum precision. Clipper cut, wash and finish.", 30, "50.00", "70.00", "90.00"),
]
BARBERS = [
    ("Alex", "Classic cuts & modern shapes", "Thoughtful scissor work and easy-to-wear shapes, with attention to the little details.", "A", Barber.Level.TOP),
    ("Mika", "Texture & natural movement", "Relaxed texture, natural movement and a cut that feels as good as it looks.", "M", Barber.Level.JUNIOR),
    ("Sam", "Precision fades & beard work", "Sharp transitions, considered proportions and a clean finish from every angle.", "S", Barber.Level.SENIOR),
]
TRAINING = ("The training cut", "A haircut with a barber in training, supervised throughout by a Senior. Half the Junior price, with extra time for care and detail.")


class Command(BaseCommand):
    help = "Create reproducible fictional services, barbers and schedules. No passwords or customer data."

    @transaction.atomic
    def handle(self, *args, **options):
        services = []
        for index, (name, description, duration, price, senior_price, top_price) in enumerate(SERVICES):
            service, _ = Service.objects.update_or_create(name=name, defaults={"description": description, "duration_minutes": duration, "price": price, "senior_price": senior_price, "top_price": top_price, "training_for": None, "display_order": index, "is_active": True})
            services.append(service)
        training, _ = Service.objects.update_or_create(name=TRAINING[0], defaults={"description": TRAINING[1], "duration_minutes": 60, "price": "35.00", "training_for": services[0], "display_order": 4, "is_active": True})
        people = []
        for name, role, bio, initials, level in BARBERS:
            barber, _ = Barber.objects.update_or_create(name=name, defaults={"role": role, "bio": bio, "initials": initials, "level": level, "supervisor": None, "is_active": True})
            barber.services.set(services)
            people.append(barber)
        trainee, _ = Barber.objects.update_or_create(name="Noah", defaults={"role": "Learning the craft", "bio": "A considered haircut with extra time, guided from start to finish by Sam, our Senior barber.", "initials": "N", "level": Barber.Level.TRAINEE, "supervisor": people[2], "is_active": True})
        trainee.services.set([training])
        people.append(trainee)
        for barber in people:
            for day in range(6):
                WorkingHours.objects.update_or_create(barber=barber, weekday=day, defaults={"start_time": time(10), "end_time": time(16 if day == 5 else 19)})
                Break.objects.get_or_create(barber=barber, weekday=day, start_time=time(13), end_time=time(13, 30))
        self.stdout.write(self.style.SUCCESS("Demo catalog and weekly schedules are ready. No user accounts or passwords were created."))
