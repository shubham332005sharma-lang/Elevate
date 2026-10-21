from django.contrib import admin

from .models import Elevator, Incident


@admin.register(Elevator)
class ElevatorAdmin(admin.ModelAdmin):
    list_display = ("code", "building", "location", "is_operational")
    search_fields = ("code", "building", "location")


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ("title", "elevator", "severity", "status", "assigned_to", "created_at")
    list_filter = ("status", "severity", "elevator")
    search_fields = ("title", "description", "reporter_name", "elevator__code")
