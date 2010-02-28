from django import forms

from models import LocationType, Incident

class IncidentForm(forms.ModelForm):
    #location_type = forms.ModelMultipleChoiceField(queryset=LocationType.objects.all)
    class Meta:
        model = Incident
