from django.contrib import admin

from airlink_api.models import (
    AirplaneType,
    Airplane,
    Airport,
    Crew,
    Route,
    Flight,
    Order,
    Ticket
)
admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(Airport)
admin.site.register(Crew)
admin.site.register(Route)
admin.site.register(Flight)
admin.site.register(Order)
admin.site.register(Ticket)
