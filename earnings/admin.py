from django.contrib import admin
from .models import DriverEarning   


# Register your models here.
admin.site.register(DriverEarning)  

class DriverEarningAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "driver",
        "shipment",
        "distance_km",
        "rate_per_km",
        "amount",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "created_at", "updated_at")
    search_fields = ("driver__user__username", "shipment__tracking_number")