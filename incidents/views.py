from django.shortcuts import render_to_response
from django.template import RequestContext

from forms import IncidentForm

def incident_form(request):
    """Form for users to submit an incident"""
    if request.method == 'POST':
       f = IncidentForm(request.POST)
       if f.is_valid():
           f.save()
    else:
       f = IncidentForm()
    return render_to_response('incidents/incident_form.html', {
       'form': f
    }, context_instance=RequestContext(request))
