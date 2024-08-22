from django.urls import path, include
from rest_framework.routers import DefaultRouter

from airlink_api.views import (
    AirplaneTypeViewSet,
    AirplaneViewSet,
    AirportViewSet,
    CrewViewSet,
    RouteViewSet,
    FlightViewSet,
    OrderViewSet,
)

router = DefaultRouter()
router.register(r"airplane-types", AirplaneTypeViewSet, basename="airplane-type")
router.register(r"airplanes", AirplaneViewSet, basename="airplane")
router.register(r"airports", AirportViewSet, basename="airport")
router.register(r"crew", CrewViewSet, basename="crew")
router.register(r"routes", RouteViewSet, basename="route")
router.register(r"flights", FlightViewSet, basename="flight")
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = [path("", include(router.urls))]

app_name = "airlink_api"
