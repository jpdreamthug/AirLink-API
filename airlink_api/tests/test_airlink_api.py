from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from airlink_api.models import Airplane, Route, Flight, Crew, AirplaneType, Airport
from airlink_api.serializers import FlightListSerializer, FlightDetailSerializer
import uuid

FLIGHT_URL = reverse("airlink_api:flight-list")


def unique_name(prefix="sample"):
    return f"{prefix}_{uuid.uuid4()}"


def sample_airport(**params):
    defaults = {"name": unique_name("airport"), "closest_big_city": unique_name("city")}
    defaults.update(params)
    return Airport.objects.create(**defaults)


def sample_airplane_type(**params):
    defaults = {
        "name": unique_name("airplane_type"),
    }
    defaults.update(params)
    return AirplaneType.objects.create(**defaults)


def sample_airplane(**params):
    airplane_type = sample_airplane_type()
    defaults = {
        "name": unique_name("airplane"),
        "rows": 10,
        "seats_in_row": 6,
        "airplane_type": airplane_type,
    }
    defaults.update(params)
    return Airplane.objects.create(**defaults)


def sample_route(**params):
    source = sample_airport(name=unique_name("source"))
    destination = sample_airport(name=unique_name("destination"))
    defaults = {
        "source": source,
        "destination": destination,
        "distance": 3976,
    }
    defaults.update(params)
    return Route.objects.create(**defaults)


def sample_crew(**params):
    defaults = {
        "first_name": unique_name("crew_first"),
        "last_name": unique_name("crew_last"),
    }
    defaults.update(params)
    return Crew.objects.create(**defaults)


def sample_flight(**params):
    airplane = sample_airplane()
    route = sample_route()
    crew = sample_crew()
    defaults = {
        "departure_time": timezone.now() + timedelta(hours=2),
        "arrival_time": timezone.now() + timedelta(hours=5),
        "airplane": airplane,
        "route": route,
    }
    defaults.update(params)
    flight = Flight.objects.create(**defaults)
    flight.crew.add(crew)
    return flight


def detail_url(flight_id):
    return reverse("airlink_api:flight-detail", args=[flight_id])


class UnauthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_flights(self):
        flight1 = sample_flight()
        flight2 = sample_flight()

        res = self.client.get(FLIGHT_URL)

        for flight_data in res.data["results"]:
            flight_data.pop("tickets_available", None)
        serializer = FlightListSerializer([flight1, flight2], many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_flights_by_airplane(self):
        airplane1 = sample_airplane(name="Boeing 777")
        airplane2 = sample_airplane(name="Airbus A320")

        flight1 = sample_flight(airplane=airplane1)
        flight2 = sample_flight(airplane=airplane2)
        flight3 = sample_flight()

        res = self.client.get(FLIGHT_URL, {"id": f"{airplane1.id}"})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)

    def test_filter_flights_by_route(self):
        route1 = sample_route()

        flight1 = sample_flight(route=route1)
        flight2 = sample_flight()

        res = self.client.get(FLIGHT_URL, {"route__id": f"{route1.id}"})
        for flight_data in res.data["results"]:
            flight_data.pop("tickets_available", None)
        serializer1 = FlightListSerializer(flight1)
        serializer2 = FlightListSerializer(flight2)

        self.assertIn(serializer1.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])

    def test_retrieve_flight_detail(self):
        flight = sample_flight()
        flight.route = sample_route()
        flight.save()

        url = detail_url(flight.id)
        res = self.client.get(url)
        res.data.pop("tickets_available", None)
        serializer = FlightDetailSerializer(flight)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_flight_forbidden(self):
        payload = {
            "flight_number": "AA107",
            "departure_time": timezone.now() + timedelta(hours=2),
            "arrival_time": timezone.now() + timedelta(hours=5),
            "airplane": sample_airplane().id,
            "route": sample_route().id,
        }
        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_flight(self):
        crew = sample_crew()
        payload = {
            "departure_time": timezone.now() + timedelta(hours=2),
            "arrival_time": timezone.now() + timedelta(hours=5),
            "airplane": sample_airplane().id,
            "route": sample_route().id,
            "crew": [crew.id],
        }
        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        flight = Flight.objects.get(id=res.data["id"])

        self.assertEqual(payload["departure_time"], flight.departure_time)
        self.assertEqual(payload["arrival_time"], flight.arrival_time)

        self.assertEqual(payload["airplane"], flight.airplane.id)
        self.assertEqual(payload["route"], flight.route.id)

        self.assertEqual(
            list(flight.crew.values_list("id", flat=True)), payload["crew"]
        )
