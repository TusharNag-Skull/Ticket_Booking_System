import random
from datetime import date, timedelta, time

from django.core.management.base import BaseCommand

from booking.models import TravelOption


class Command(BaseCommand):
    help = "Seed the database with many TravelOption entries (India-heavy)."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=75, help="How many rows to add")
        parser.add_argument(
            "--clear", action="store_true", help="Delete existing TravelOption entries first"
        )

    def handle(self, *args, **options):
        count: int = options["count"]
        clear: bool = options["clear"]

        if clear:
            TravelOption.objects.all().delete()

        indian_cities = [
            "Delhi",
            "Mumbai",
            "Bengaluru",
            "Hyderabad",
            "Ahmedabad",
            "Chennai",
            "Kolkata",
            "Surat",
            "Pune",
            "Jaipur",
            "Lucknow",
            "Kanpur",
            "Nagpur",
            "Indore",
            "Thane",
            "Bhopal",
            "Visakhapatnam",
            "Patna",
            "Vadodara",
            "Ghaziabad",
            "Ludhiana",
            "Agra",
            "Nashik",
            "Faridabad",
            "Meerut",
            "Rajkot",
            "Varanasi",
            "Amritsar",
            "Prayagraj",
            "Ranchi",
            "Coimbatore",
            "Kochi",
            "Madurai",
            "Guwahati",
        ]

        other_cities = [
            "New York",
            "Los Angeles",
            "San Francisco",
            "London",
            "Paris",
            "Berlin",
            "Tokyo",
            "Singapore",
            "Dubai",
            "Sydney",
            "Toronto",
        ]

        types = ["Flight", "Train", "Bus"]

        all_cities = indian_cities * 3 + other_cities  # weight towards India

        base_date = date.today() + timedelta(days=30)
        created = 0
        for i in range(count):
            src = dst = None
            # ensure source and destination differ
            while not src or src == dst:
                src = random.choice(all_cities)
                dst = random.choice(all_cities)

            d = base_date + timedelta(days=random.randint(0, 90))
            t = time(hour=random.choice([6, 8, 9, 10, 12, 14, 16, 18, 21]), minute=0)
            price = round(random.uniform(10, 299.99), 2)
            seats = random.choice([40, 50, 60, 80, 120])

            TravelOption.objects.create(
                type=random.choice(types),
                source=src,
                destination=dst,
                departure_date=d,
                departure_time=t,
                price=price,
                available_seats=seats,
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} travel options."))


