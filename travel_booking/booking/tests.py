from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import TravelOption, Booking
from datetime import date, time


class BookingModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pass12345")
        self.travel = TravelOption.objects.create(
            type="Flight",
            source="A",
            destination="B",
            departure_date=date(2025, 12, 20),
            departure_time=time(10, 30),
            price=100,
            available_seats=10,
        )

    def test_total_price_calculated(self):
        booking = Booking.objects.create(
            user=self.user,
            travel_option=self.travel,
            number_of_seats=3,
            total_price=0,
        )
        self.assertEqual(booking.total_price, 300)


class BookingViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="bob", password="pass12345")
        self.travel = TravelOption.objects.create(
            type="Train",
            source="X",
            destination="Y",
            departure_date=date(2025, 12, 21),
            departure_time=time(9, 0),
            price=50,
            available_seats=5,
        )

    def test_travel_list(self):
        resp = self.client.get(reverse("booking:travel_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Find Travel Options")

    def test_booking_requires_login(self):
        resp = self.client.get(reverse("booking:create_booking", args=[self.travel.id]))
        self.assertEqual(resp.status_code, 302)

    def test_create_booking_reduces_seats(self):
        self.client.login(username="bob", password="pass12345")
        resp = self.client.post(
            reverse("booking:create_booking", args=[self.travel.id]),
            {"number_of_seats": 2},
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.travel.refresh_from_db()
        self.assertEqual(self.travel.available_seats, 3)
        self.assertEqual(Booking.objects.filter(user=self.user).count(), 1)


# Create your tests here.
