from django.db import models
from django.contrib.auth import get_user_model


class TravelOption(models.Model):
    class TravelType(models.TextChoices):
        FLIGHT = "Flight", "Flight"
        TRAIN = "Train", "Train"
        BUS = "Bus", "Bus"

    type = models.CharField(max_length=10, choices=TravelType.choices)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_date = models.DateField()
    departure_time = models.TimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_seats = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.type} {self.source} -> {self.destination} on {self.departure_date} {self.departure_time}"


User = get_user_model()


class Booking(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = "Confirmed", "Confirmed"
        CANCELLED = "Cancelled", "Cancelled"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    travel_option = models.ForeignKey(TravelOption, on_delete=models.CASCADE)
    number_of_seats = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.CONFIRMED)

    def __str__(self) -> str:
        return f"Booking #{self.pk} - {self.user} - {self.travel_option}"

    def calculate_total_price(self) -> None:
        self.total_price = self.number_of_seats * self.travel_option.price

    def save(self, *args, **kwargs):
        # Ensure total price is always in sync before saving
        self.calculate_total_price()
        super().save(*args, **kwargs)


# Create your models here.
