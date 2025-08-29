from django.urls import path
from . import views

app_name = "booking"

urlpatterns = [
    path("", views.travel_list, name="travel_list"),
    path("type/<str:travel_type>/", views.travel_list_by_type, name="travel_list_by_type"),
    path("book/<int:travel_id>/", views.create_booking, name="create_booking"),
    path("bookings/", views.booking_history, name="booking_history"),
    path("cancel/<int:booking_id>/", views.cancel_booking, name="cancel_booking"),
    path("api/suggest/", views.suggest_locations, name="suggest_locations"),
]


