from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint


class AirplaneType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255, unique=True)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()
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
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

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
            UniqueConstraint(fields=['source', 'destination'], name='unique_route'),
        ]

    def __str__(self):
        return f"{self.source.name} - {self.destination.name}"


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

    def __str__(self):
        return f"{self.airplane.name} on {self.route}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="orders",
    )

    def __str__(self):
        return f"Order created at {self.created_at} by user {self.user.id}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight, on_delete=models.SET_NULL, null=True, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, null=True, related_name="tickets"
    )

    def __str__(self):
        return f"Flight: {self.flight}, Row: {self.row}, Seat: {self.seat}"
