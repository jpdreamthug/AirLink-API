from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint, Q
from django.utils import timezone


class AirplaneType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255, unique=True)
    rows = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    seats_in_row = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    airplane_type = models.ForeignKey(
        AirplaneType, on_delete=models.CASCADE, related_name="airplanes"
    )

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=255, unique=True)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self):
        return str(self.name)


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    @property
    def full_name(self):
        return str(self)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="departure_routes"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="arrival_routes"
    )
    distance = models.PositiveIntegerField()

    class Meta:
        constraints = [
            UniqueConstraint(fields=["source", "destination"], name="unique_route"),
        ]

    @property
    def get_route(self):
        return str(self)

    def __str__(self):
        return f"{self.source} - {self.destination}"


class Flight(models.Model):
    route = models.ForeignKey(
        Route, on_delete=models.SET_NULL, null=True, related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane, on_delete=models.SET_NULL, null=True, related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew)

    @staticmethod
    def validate_time(arrival_time, departure_time):
        if arrival_time <= departure_time:
            raise ValidationError(
                {"arrival_time": "Arrival time must be later than departure time."}
            )

        flight_duration = arrival_time - departure_time
        if flight_duration > timedelta(hours=24):
            raise ValidationError(
                {"arrival_time": "Flight duration cannot exceed 24 hours."}
            )

        if departure_time <= timezone.now():
            raise ValidationError(
                {"departure_time": "Departure time must be in the future."}
            )

        if departure_time <= timezone.now() + timedelta(hours=1):
            raise ValidationError(
                {
                    "departure_time": "Departure time must be at least one hour later than the current time."
                }
            )

    @staticmethod
    def validate_crew_availability(
        crew, departure_time, arrival_time, exclude_flight_id=None
    ):
        for crew_member in crew:
            conflicting_flights = Flight.objects.filter(
                Q(crew=crew_member)
                & Q(departure_time__lt=arrival_time)
                & Q(arrival_time__gt=departure_time)
            )
            if exclude_flight_id:
                conflicting_flights = conflicting_flights.exclude(pk=exclude_flight_id)

            if conflicting_flights.exists():
                raise ValidationError(
                    f"Crew member {crew_member} is not available for this flight time. "
                    f"They already have an assigned flight during this period."
                )

    def clean(self):
        super().clean()
        self.validate_time(self.arrival_time, self.departure_time)
        if self.pk:
            self.validate_crew_availability(
                self.crew.all(), self.departure_time, self.arrival_time, self.pk
            )
        else:
            self.validate_crew_availability(
                self.crew.all(), self.departure_time, self.arrival_time
            )

    def __str__(self):
        return f"{self.airplane.name} on route {self.route}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="orders",
    )

    def __str__(self):
        return f"Order created at {self.created_at} by user {self.user}"


class Ticket(models.Model):
    row = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    seat = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    flight = models.ForeignKey(
        Flight, on_delete=models.SET_NULL, null=True, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, null=True, related_name="tickets"
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["row", "seat", "flight"], name="unique_ticket_seat_row_flight"
            )
        ]

    @staticmethod
    def validate_seat(row, seat, flight):
        if row > flight.airplane.rows or seat > flight.airplane.seats_in_row:
            raise ValidationError(
                {
                    "row": f"Row must be between 1 and {flight.airplane.rows}",
                    "seat": f"Seat must be between 1 and {flight.airplane.seats_in_row}",
                }
            )

    def clean(self):
        super().clean()
        self.validate_seat(self.row, self.seat, self.flight)

    def __str__(self):
        return f"Flight: {self.flight}, Row: {self.row}, Seat: {self.seat}"
