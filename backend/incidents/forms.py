from django import forms

from .models import Elevator, Incident


class IncidentReportForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ["elevator", "title", "description", "category", "severity", "reporter_name", "reporter_contact"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "reporter_contact": forms.TextInput(attrs={"autocomplete": "tel"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["elevator"].queryset = Elevator.objects.all()


class IncidentUpdateForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ["status", "severity", "assigned_to"]
