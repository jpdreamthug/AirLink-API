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
router.register(r"airplane-types", AirplaneTypeViewSet, basename="airplane-types")
router.register(r"airplanes", AirplaneViewSet, basename="airplanes")
router.register(r"airports", AirportViewSet, basename="airports")
router.register(r"crew", CrewViewSet, basename="crew")
router.register(r"routes", RouteViewSet, basename="routes")
router.register(r"flights", FlightViewSet, basename="flights")
router.register(r"orders", OrderViewSet, basename="orders")

urlpatterns = [path("", include(router.urls))]

app_name = "airlink_api"
