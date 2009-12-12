# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.template import RequestContext, loader, Template, Context
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from myproject.sms.models import SMS
from datetime import datetime

def post(request):

    if request.method == "POST": get = request.POST
    elif request.method == 'GET': get = request.GET
    else: get = None

    if get and get.__contains__('user') and get['user'] != "":
        
        user = get['user']
        
        if get.__contains__('text'):
            
            text = get['text']
            mes = SMS(phone_number=user, message=text, timestamp=datetime.utcnow())
            mes.save()  
	    return HttpResponse(status=201)
    
    return render_to_response('post_error.html', context_instance=RequestContext(request))

def index(request):
    
    texts = SMS.objects.all()
    return render_to_response('index.html', {'texts': texts}) 
