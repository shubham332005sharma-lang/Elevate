from django import forms

from .models import Elevator, Incident


class IncidentReportForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ["elevator", "title", "description", "category", "severity", "reporter_name", "reporter_contact"]
        labels = {
            "elevator": "Elevator",
            "title": "Issue title",
            "description": "What happened?",
            "category": "Issue category",
            "severity": "How urgent is it?",
            "reporter_name": "Your name",
            "reporter_contact": "Phone or email (optional)",
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "For example: Elevator door will not close"}),
            "description": forms.Textarea(attrs={"rows": 4}),
            "reporter_name": forms.TextInput(attrs={"autocomplete": "name"}),
            "reporter_contact": forms.TextInput(attrs={"autocomplete": "tel", "placeholder": "How can staff contact you?"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["elevator"].queryset = Elevator.objects.all()


class IncidentUpdateForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ["status", "severity", "assigned_to"]
