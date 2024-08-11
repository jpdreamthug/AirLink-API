import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from airlink_api.models import (
    AirplaneType,
    Airplane,
    Airport,
    Crew,
    Route,
    Flight,
)


class Command(BaseCommand):
    help = "Creates sample data for the airlink app"

    def handle(self, *args, **kwargs):
        airplane_types = [
            AirplaneType.objects.create(name="Boeing 737"),
            AirplaneType.objects.create(name="Airbus A320"),
            AirplaneType.objects.create(name="Embraer E175"),
            AirplaneType.objects.create(name="Bombardier CRJ900"),
            AirplaneType.objects.create(name="Airbus A350"),
        ]

        airplanes = []
        for i in range(15):
            airplane_type = random.choice(airplane_types)
            airplanes.append(
                Airplane.objects.create(
                    name=f"Plane-{i + 1}",
                    rows=random.randint(20, 40),
                    seats_in_row=random.choice([4, 6]),
                    airplane_type=airplane_type,
                )
            )

        airports = [
            Airport.objects.create(
                name="Boryspil International Airport", closest_big_city="Kyiv"
            ),
            Airport.objects.create(
                name="Barcelona–El Prat Airport", closest_big_city="Barcelona"
            ),
            Airport.objects.create(name="Heathrow Airport", closest_big_city="London"),
            Airport.objects.create(
                name="Charles de Gaulle Airport", closest_big_city="Paris"
            ),
            Airport.objects.create(
                name="Frankfurt Airport", closest_big_city="Frankfurt"
            ),
            Airport.objects.create(
                name="Schiphol Airport", closest_big_city="Amsterdam"
            ),
            Airport.objects.create(
                name="Leonardo da Vinci International Airport", closest_big_city="Rome"
            ),
            Airport.objects.create(
                name="Istanbul Airport", closest_big_city="Istanbul"
            ),
        ]

        crews = []
        first_names = [
            "John",
            "Jane",
            "Mike",
            "Emily",
            "David",
            "Sarah",
            "Alex",
            "Olivia",
            "Daniel",
            "Sophia",
        ]
        last_names = [
            "Smith",
            "Johnson",
            "Williams",
            "Brown",
            "Jones",
            "Garcia",
            "Miller",
            "Davis",
            "Rodriguez",
            "Martinez",
        ]
        for _ in range(30):
            crews.append(
                Crew.objects.create(
                    first_name=random.choice(first_names),
                    last_name=random.choice(last_names),
                )
            )

        routes = []
        for source in airports:
            for destination in airports:
                if source != destination:
                    routes.append(
                        Route.objects.create(
                            source=source,
                            destination=destination,
                            distance=random.randint(500, 3000),
                        )
                    )

        now = timezone.now()
        flights = []
        for _ in range(50):
            route = random.choice(routes)
            airplane = random.choice(airplanes)
            departure_time = now + timedelta(days=random.randint(1, 30))
            flight = Flight.objects.create(
                route=route,
                airplane=airplane,
                departure_time=departure_time,
                arrival_time=departure_time + timedelta(hours=random.randint(1, 8)),
            )
            flight.crew.set(random.sample(crews, k=random.randint(3, 5)))
            flights.append(flight)

        self.stdout.write(self.style.SUCCESS("Sample data created successfully"))
