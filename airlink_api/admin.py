from django.contrib import admin

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


class FlightAdmin(admin.ModelAdmin):

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)


admin.site.register(Flight, FlightAdmin)
admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(Airport)
admin.site.register(Crew)
admin.site.register(Route)
admin.site.register(Order)
admin.site.register(Ticket)
