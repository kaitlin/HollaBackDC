from django.conf import settings
from django.core import urlresolvers

from django.conf.urls import defaults
defaults.handler503 = 'maintenancemode.views.temporary_unavailable'
defaults.__all__.append('handler503')

class MaintenanceModeMiddleware(object):
    def process_request(self, request):
        # Check if maintenance mode is activated, if not set default to False
        if getattr(settings, 'MAINTENANCE_MODE', False):
            # Check if the user doing the request is logged in and a staff member
            if ((hasattr(request, 'user') and request.user.is_staff) or
                request.path == '/admin/'):
                # Let Django normally handle the request
                return None

            # Otherwise show the user the 503 page
            resolver = urlresolvers.get_resolver(None)

            callback, param_dict = resolver._resolve_special('503')
            return callback(request, **param_dict)
