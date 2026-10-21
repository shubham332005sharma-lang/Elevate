from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import IncidentReportForm, IncidentUpdateForm
from .models import Incident


def home(request):
    return render(request, "incidents/home.html")


def report_incident(request):
    if request.method == "POST":
        form = IncidentReportForm(request.POST)
        if form.is_valid():
            incident = form.save()
            return render(request, "incidents/report_success.html", {"incident": incident})
    else:
        form = IncidentReportForm()
    return render(request, "incidents/report_issue.html", {"form": form})


@login_required
def incident_list(request):
    incidents = Incident.objects.select_related("elevator", "assigned_to")
    return render(request, "incidents/incident_list.html", {"incidents": incidents})


@login_required
def incident_detail(request, pk):
    incident = get_object_or_404(Incident.objects.select_related("elevator", "assigned_to"), pk=pk)
    if request.method == "POST":
        form = IncidentUpdateForm(request.POST, instance=incident)
        if form.is_valid():
            form.save()
            messages.success(request, "Incident updated.")
            return redirect("incident-detail", pk=incident.pk)
    else:
        form = IncidentUpdateForm(instance=incident)
    return render(request, "incidents/incident_detail.html", {"incident": incident, "form": form})
