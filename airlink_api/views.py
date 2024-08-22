from django.db.models import F, Count, Value
from django.db.models.functions import Concat
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

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
from airlink_api.permissions import IsAdminOrIfAuthenticatedReadOnly
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
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ["name"]
    search_fields = ["name"]
    pagination_class = BasePagination


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related("airplane_type")
    serializer_class = AirplaneSerializer
    action_serializers = {
        "list": AirplaneListSerializer,
        "retrieve": AirplaneDetailSerializer,
    }
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ["name"]
    search_fields = ["name"]
    pagination_class = BasePagination


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ["name", "closest_big_city"]
    search_fields = ["name", "closest_big_city"]
    pagination_class = BasePagination


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ["first_name", "last_name"]
    search_fields = ["first_name", "last_name"]
    pagination_class = BasePagination


class RouteViewSet(GenericMethodsMixin, viewsets.ModelViewSet):
    pagination_class = BasePagination
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer
    action_serializers = {
        "list": RouteListSerializer,
        "retrieve": RouteDetailSerializer,
    }
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["source__name", "destination__name"]


class FlightViewSet(GenericMethodsMixin, viewsets.ModelViewSet):
    pagination_class = BasePagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["departure_time", "arrival_time", "id", "route__id"]
    serializer_class = FlightSerializer
    action_serializers = {
        "list": FlightListSerializer,
        "retrieve": FlightDetailSerializer,
    }
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = (
            Flight.objects.select_related(
                "airplane__airplane_type",
                "route__source",
                "route__destination",
            )
            .prefetch_related(
                "crew",
            )
            .annotate(
                tickets_available=(
                    F("airplane__rows") * F("airplane__seats_in_row") - Count("tickets")
                ),
                custom_route=Concat(
                    F("route__source__name"),
                    Value(" - "),
                    F("route__destination__name"),
                ),
            )
        )
        return queryset


class OrderViewSet(GenericMethodsMixin, viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related("tickets")
    pagination_class = BasePagination
    serializer_class = OrderSerializer
    action_serializers = {
        "retrieve": OrderDetailSerializer,
    }
    permission_classes = (IsAuthenticated,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ["created_at"]
    search_fields = ["tickets__flight"]

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
