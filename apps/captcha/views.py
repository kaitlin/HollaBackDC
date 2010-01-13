# -*- mode: python; coding: utf-8; -*-

# Original: http://django-pantheon.googlecode.com/svn/trunk/pantheon/supernovaforms/

from django.http import HttpResponse
import captcha

def captcha_image(request, captcha_id):
    response = HttpResponse(mimetype='image/jpeg')
    captcha.render(captcha_id, response)
    return response
