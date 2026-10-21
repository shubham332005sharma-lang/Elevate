from django.conf import settings
from django.db import models


class Elevator(models.Model):
    code = models.CharField(max_length=20, unique=True)
    building = models.CharField(max_length=120, blank=True)
    location = models.CharField(max_length=200, blank=True)
    is_operational = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.code


class Incident(models.Model):
    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        INVESTIGATING = "investigating", "Investigating"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    elevator = models.ForeignKey(Elevator, on_delete=models.PROTECT, related_name="incidents")
    title = models.CharField(max_length=160)
    description = models.TextField()
    category = models.CharField(max_length=80, blank=True)
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.MEDIUM)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    reporter_name = models.CharField(max_length=120)
    reporter_contact = models.CharField(max_length=160, blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_incidents",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.elevator.code}: {self.title}"
