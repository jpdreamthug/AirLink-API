from django.db.models import F, Count, Value
from django.db.models.functions import Concat
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from airlink_api.mixins import GenericMethodsMixin
from airlink_api.models import (
    AirplaneType,
    Airplane,
    Airport,
    Crew,
    Route,
    Flight,
    Order,
)
from airlink_api.serializers import (
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirportSerializer,
    CrewSerializer,
    RouteSerializer,
    FlightSerializer,
    OrderSerializer,
    AirplaneListSerializer,
    AirplaneDetailSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    OrderDetailSerializer,
)


class BasePagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(GenericMethodsMixin, viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related("airplane_type")
    serializer_class = AirplaneSerializer
    action_serializers = {
        "list": AirplaneListSerializer,
        "retrieve": AirplaneDetailSerializer,
    }


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class RouteViewSet(GenericMethodsMixin, viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer
    action_serializers = {
        "list": RouteListSerializer,
        "retrieve": RouteDetailSerializer,
    }


class FlightViewSet(GenericMethodsMixin, viewsets.ModelViewSet):
    serializer_class = FlightSerializer
    action_serializers = {
        "list": FlightListSerializer,
        "retrieve": FlightDetailSerializer,
    }

    def get_queryset(self):
        queryset = Flight.objects.select_related(
            "airplane__airplane_type",
            "route__source",
            "route__destination",
        ).prefetch_related(
            "crew",
        ).annotate(
            tickets_available=(
                    F("airplane__rows") * F("airplane__seats_in_row") - Count("tickets")
            ),
            custom_route=Concat(
                F("route__source__name"),
                Value(" - "),
                F("route__destination__name"),
            ),
        )
        return queryset


class OrderViewSet(GenericMethodsMixin, viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related("tickets")
    pagination_class = BasePagination
    serializer_class = OrderSerializer
    action_serializers = {
        "retrieve": OrderDetailSerializer,
    }

    def get_queryset(self):
        queryset = self.queryset

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        user_id = self.request.query_params.get("user", None)
        if user_id:
            queryset = queryset.filter(user__id=user_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
