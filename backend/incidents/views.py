from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django import forms
import json

from .forms import IncidentReportForm, IncidentUpdateForm
from .models import Elevator, Incident


class TechnicianTaskForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ["status"]


def home(request):
    if request.user.is_authenticated:
        # The requested app entry behavior is a fresh sign-in each time / is opened.
        logout(request)
    return redirect("login")


def staff_role_required(view):
    def has_staff_role(user):
        return user.is_authenticated and (
            user.is_superuser or user.groups.filter(name__in=["Administrator", "Technician"]).exists()
        )

    return user_passes_test(has_staff_role, login_url="login")(view)


def is_technician(user):
    return not user.is_superuser and user.groups.filter(name="Technician").exists()


@staff_role_required
def dashboard(request):
    if is_technician(request.user):
        tasks = Incident.objects.filter(assigned_to=request.user).select_related("elevator", "assigned_to")
        return render(request, "incidents/technician/dashboard.html", {
            "tasks": tasks,
            "active_task_count": tasks.exclude(status__in=[Incident.Status.RESOLVED, Incident.Status.CLOSED]).count(),
        })
    active_incidents = Incident.objects.exclude(status__in=[Incident.Status.RESOLVED, Incident.Status.CLOSED])
    context = {
        "total_elevators": Elevator.objects.count(),
        "operational_elevators": Elevator.objects.filter(is_operational=True).count(),
        "warning_incidents": active_incidents.filter(severity__in=[Incident.Severity.MEDIUM, Incident.Severity.HIGH]).count(),
        "critical_incidents": active_incidents.filter(severity=Incident.Severity.CRITICAL).count(),
        "active_incident_count": active_incidents.count(),
        "elevators": Elevator.objects.all()[:4],
        "recent_incidents": Incident.objects.select_related("elevator")[:3],
    }
    return render(request, "incidents/administrator/dashboard.html", context)


@staff_role_required
def elevator_list(request):
    if is_technician(request.user):
        return redirect("dashboard")
    elevators = Elevator.objects.all()
    return render(request, "incidents/administrator/elevators.html", {"elevators": elevators})


def report_incident(request):
    elevator_count = Elevator.objects.count()
    if request.method == "POST":
        form = IncidentReportForm(request.POST)
        if form.is_valid():
            incident = form.save()
            return render(request, "incidents/public/report_success.html", {"incident": incident})
    else:
        form = IncidentReportForm()
    return render(request, "incidents/public/report_issue.html", {"form": form, "elevator_count": elevator_count})


@staff_role_required
def incident_list(request):
    if is_technician(request.user):
        return redirect("dashboard")
    all_incidents = Incident.objects.select_related("elevator", "assigned_to")
    incidents = all_incidents
    search = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    severity = request.GET.get("severity", "")
    elevator_id = request.GET.get("elevator", "")
    if search:
        incidents = incidents.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(elevator__code__icontains=search)
            | Q(category__icontains=search)
        )
    if status:
        incidents = incidents.filter(status=status)
    if severity:
        incidents = incidents.filter(severity=severity)
    if elevator_id:
        incidents = incidents.filter(elevator_id=elevator_id)
    active_incidents = all_incidents.exclude(status__in=[Incident.Status.RESOLVED, Incident.Status.CLOSED])
    context = {
        "incidents": incidents,
        "open_count": all_incidents.filter(status=Incident.Status.OPEN).count(),
        "investigating_count": all_incidents.filter(status=Incident.Status.INVESTIGATING).count(),
        "resolved_count": all_incidents.filter(status=Incident.Status.RESOLVED).count(),
        "active_count": active_incidents.count(),
        "total_count": all_incidents.count(),
        "elevators": Elevator.objects.all(),
        "search": search,
        "selected_status": status,
        "selected_severity": severity,
        "selected_elevator": elevator_id,
        "status_choices": Incident.Status.choices,
        "severity_choices": Incident.Severity.choices,
    }
    return render(request, "incidents/administrator/incidents.html", context)


@staff_role_required
def incident_detail(request, pk):
    incident = get_object_or_404(Incident.objects.select_related("elevator", "assigned_to"), pk=pk)
    technician = is_technician(request.user)
    if technician and incident.assigned_to_id != request.user.id:
        from django.http import Http404
        raise Http404
    if request.method == "POST":
        form_class = TechnicianTaskForm if technician else IncidentUpdateForm
        form = form_class(request.POST, instance=incident)
        if form.is_valid():
            form.save()
            messages.success(request, "Incident updated.")
            return redirect("incident-detail", pk=incident.pk)
    else:
        form_class = TechnicianTaskForm if technician else IncidentUpdateForm
        form = form_class(instance=incident)
    return render(request, "incidents/shared/incident_detail.html", {"incident": incident, "form": form, "technician": technician})


@csrf_exempt
def device_incident_api(request):
    """Accept sensor incidents from an ESP32 using JSON and an X-Device-Token."""
    from django.conf import settings

    if request.method != "POST":
        return JsonResponse({"error": "Use POST with a JSON body."}, status=405)
    expected_token = getattr(settings, "DEVICE_API_TOKEN", "")
    if not expected_token:
        return JsonResponse({"error": "Device API is not configured. Set ELEVATE_DEVICE_API_TOKEN."}, status=503)
    if request.headers.get("X-Device-Token") != expected_token:
        return JsonResponse({"error": "Invalid or missing device token."}, status=401)
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Request body must be valid JSON."}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({"error": "JSON body must be an object."}, status=400)
    code = str(payload.get("elevator_code", "")).strip()
    title = str(payload.get("title", "")).strip()
    description = str(payload.get("description", "")).strip()
    if not code or not title or not description:
        return JsonResponse({"error": "elevator_code, title, and description are required."}, status=400)
    elevator = Elevator.objects.filter(code=code).first()
    if elevator is None:
        return JsonResponse({"error": f"Unknown elevator_code: {code}"}, status=404)
    severity = payload.get("severity", Incident.Severity.HIGH)
    if severity not in Incident.Severity.values:
        return JsonResponse({"error": "severity must be low, medium, high, or critical."}, status=400)
    incident = Incident.objects.create(
        elevator=elevator,
        title=title[:160],
        description=description,
        category=str(payload.get("category", "Sensor alert"))[:80],
        severity=severity,
        reporter_name=str(payload.get("device_id", "ESP32 device"))[:120],
    )
    return JsonResponse({"id": incident.pk, "status": incident.status, "message": "Incident created."}, status=201)
