from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse

from .forms import SearchForm, BookingForm
from .models import TravelOption, Booking


def travel_list(request):
    form = SearchForm(request.GET or None)
    queryset = TravelOption.objects.all().order_by("departure_date", "departure_time")

    if form.is_valid():
        type_val = form.cleaned_data.get("type")
        source = form.cleaned_data.get("source")
        destination = form.cleaned_data.get("destination")
        date = form.cleaned_data.get("date")

        if type_val:
            queryset = queryset.filter(type=type_val)
        if source:
            queryset = queryset.filter(source__icontains=source)
        if destination:
            queryset = queryset.filter(destination__icontains=destination)
        if date:
            queryset = queryset.filter(departure_date=date)

    # Popular routes: based on today's bookings (or recent 24h)
    from django.utils import timezone
    from datetime import timedelta
    since = timezone.now() - timedelta(days=1)
    popular_qs = (
        Booking.objects.filter(booking_date__gte=since)
        .values("travel_option__source", "travel_option__destination")
        .order_by()
    )
    # Build counts dictionary
    counts = {}
    for item in popular_qs:
        key = (item["travel_option__source"], item["travel_option__destination"])
        counts[key] = counts.get(key, 0) + 1
    popular = [
        {"source": s, "destination": d, "count": c}
        for (s, d), c in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:6]
    ]

    context = {"form": form, "travel_options": queryset, "popular_routes": popular}
    return render(request, "booking/travel_list.html", context)


def travel_list_by_type(request, travel_type: str):
    # reuse search form but lock the type
    request_get = request.GET.copy()
    request_get["type"] = travel_type.capitalize()
    form = SearchForm(request_get)
    queryset = (
        TravelOption.objects.filter(type=travel_type.capitalize())
        .order_by("departure_date", "departure_time")
    )
    if form.is_valid():
        source = form.cleaned_data.get("source")
        destination = form.cleaned_data.get("destination")
        date = form.cleaned_data.get("date")
        if source:
            queryset = queryset.filter(source__icontains=source)
        if destination:
            queryset = queryset.filter(destination__icontains=destination)
        if date:
            queryset = queryset.filter(departure_date=date)
    context = {"form": form, "travel_options": queryset, "popular_routes": []}
    return render(request, "booking/travel_list_by_type.html", context)


@login_required
@transaction.atomic
def create_booking(request, travel_id: int):
    # Lock the row to prevent concurrent overbooking
    travel_option = (
        TravelOption.objects.select_for_update().select_related(None).get(pk=travel_id)
    )
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            number_of_seats = form.cleaned_data["number_of_seats"]
            passenger_name = form.cleaned_data["primary_passenger_name"].strip()
            passenger_age = form.cleaned_data["primary_passenger_age"]
            if number_of_seats <= 0:
                messages.error(request, "Number of seats must be positive.")
            elif travel_option.available_seats < number_of_seats:
                messages.error(request, "Not enough seats available.")
            else:
                booking = Booking.objects.create(
                    user=request.user,
                    travel_option=travel_option,
                    number_of_seats=number_of_seats,
                    primary_passenger_name=passenger_name,
                    primary_passenger_age=passenger_age,
                    passenger_details=form.cleaned_data.get("passenger_details", []),
                    total_price=0,
                )
                # Atomic seat decrement
                TravelOption.objects.filter(pk=travel_option.pk).update(
                    available_seats=F("available_seats") - number_of_seats
                )
                # Send confirmation email (best-effort)
                if request.user.email:
                    try:
                        send_mail(
                            subject="Booking Confirmed",
                            message=(
                                f"Your booking #{booking.pk} for {travel_option.type} "
                                f"{travel_option.source} -> {travel_option.destination} on "
                                f"{travel_option.departure_date} {travel_option.departure_time} is confirmed."
                            ),
                            from_email=None,
                            recipient_list=[request.user.email],
                            fail_silently=True,
                        )
                    except Exception:
                        pass
                display_name = (request.user.get_full_name() or request.user.get_username()).strip()
                messages.success(request, f"Booking confirmed, {display_name}!")
                return redirect("booking:booking_history")
    else:
        form = BookingForm()

    return render(request, "booking/booking_form.html", {"form": form, "travel_option": travel_option})


@login_required
def booking_history(request):
    bookings = (
        Booking.objects.filter(user=request.user)
        .select_related("travel_option")
        .order_by("-booking_date")
    )
    return render(request, "booking/booking_history.html", {"bookings": bookings})


@login_required
@transaction.atomic
def cancel_booking(request, booking_id: int):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    if booking.status == Booking.Status.CANCELLED:
        messages.info(request, "Booking already cancelled.")
        return redirect("booking:booking_history")

    # Restore seats with row lock
    travel = TravelOption.objects.select_for_update().get(pk=booking.travel_option_id)
    TravelOption.objects.filter(pk=travel.pk).update(
        available_seats=F("available_seats") + booking.number_of_seats
    )
    booking.status = Booking.Status.CANCELLED
    booking.save()
    if request.user.email:
        try:
            send_mail(
                subject="Booking Cancelled",
                message=(
                    f"Your booking #{booking.pk} for {travel.type} {travel.source} -> {travel.destination} "
                    f"on {travel.departure_date} {travel.departure_time} has been cancelled."
                ),
                from_email=None,
                recipient_list=[request.user.email],
                fail_silently=True,
            )
        except Exception:
            pass
    display_name = (request.user.get_full_name() or request.user.get_username()).strip()
    messages.success(request, f"Booking cancelled and seats restored, {display_name}.")
    return redirect("booking:booking_history")


def suggest_locations(request):
    """Return JSON suggestions for source/destination.
    Query params: q=term, field=source|destination (optional)
    """
    term = (request.GET.get("q") or "").strip()
    field = (request.GET.get("field") or "").strip().lower()
    qs = TravelOption.objects.all()
    if field == "source":
        values_qs = qs.values_list("source", flat=True)
    elif field == "destination":
        values_qs = qs.values_list("destination", flat=True)
    else:
        values_qs = qs.values_list("source", flat=True)
        values_qs = list(values_qs) + list(qs.values_list("destination", flat=True))

    if term:
        values = [v for v in values_qs if term.lower() in v.lower()]
    else:
        values = list(values_qs)
    # unique, preserve order
    seen = set()
    unique_values = []
    for v in values:
        if v not in seen:
            seen.add(v)
            unique_values.append(v)
        if len(unique_values) >= 10:
            break
    return JsonResponse({"results": unique_values})
