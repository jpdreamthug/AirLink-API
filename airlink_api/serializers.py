from django.db import transaction
from rest_framework import serializers

from airlink_api.models import (
    AirplaneType,
    Airplane,
    Airport,
    Crew,
    Route,
    Flight,
    Order,
    Ticket,
)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type")


class AirplaneListSerializer(serializers.ModelSerializer):
    airplane_model = serializers.CharField(source="airplane_type.name", read_only=True)

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_model", "capacity")


class AirplaneDetailSerializer(serializers.ModelSerializer):
    airplane_type = AirplaneTypeSerializer(read_only=True)

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type", "capacity")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")


class RouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(serializers.ModelSerializer):
    get_route = serializers.CharField(read_only=True)

    class Meta:
        model = Route
        fields = ("id", "distance", "get_route")


class RouteDetailSerializer(RouteSerializer):
    source = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "crew",
            "airplane",
            "departure_time",
            "arrival_time",
        )

    def validate(self, attrs):
        data = super().validate(attrs)

        arrival_time = attrs.get("arrival_time") or (
            self.instance.arrival_time if self.instance else None
        )
        departure_time = attrs.get("departure_time") or (
            self.instance.departure_time if self.instance else None
        )

        if arrival_time and departure_time:
            Flight.validate_time(arrival_time, departure_time)

        crew = attrs.get("crew") or (
            self.instance.crew.all() if self.instance else None
        )
        if crew and arrival_time and departure_time:
            Flight.validate_crew_availability(
                crew,
                departure_time,
                arrival_time,
                exclude_flight_id=self.instance.pk if self.instance else None,
            )

        return data


class FlightListSerializer(FlightSerializer):
    flight_route = serializers.CharField(read_only=True)
    crew = serializers.StringRelatedField(many=True)
    airplane_name = serializers.CharField(
        source="airplane.airplane_type.name", read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "crew",
            "flight_route",
            "airplane_name",
            "departure_time",
            "arrival_time",
            "tickets_available",
        )


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        Ticket.validate_seat(attrs["row"], attrs["seat"], attrs["flight"])
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "order")


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class FlightDetailSerializer(FlightSerializer):
    flight_route = serializers.CharField(read_only=True)
    crew = CrewSerializer(many=True, read_only=True)
    airplane = AirplaneDetailSerializer(read_only=True)
    tickets_available = serializers.IntegerField(read_only=True)
    taken_places = TicketSeatsSerializer(source="tickets", many=True, read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "flight_route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew",
            "tickets_available",
            "taken_places",
        )


class TicketDetailSerializer(TicketSerializer):
    flight = FlightListSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(read_only=False, many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets", "user")
        read_only_fields = (
            "id",
            "user",
        )

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderDetailSerializer(OrderSerializer):
    tickets = TicketDetailSerializer(read_only=True, many=True)
