# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.template import RequestContext, loader, Template, Context
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404

def index(request):
    #need some more stuff here later
    return render_to_response('index.html')
