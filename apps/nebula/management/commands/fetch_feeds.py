from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured
from django.db import models

from nebula.models import AggregatedBlog


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--quiet', action='store_true', dest='quiet', default=False,
                    help='No any output except error messages'),
    )
    help = "Fetch all available feeds controlled by nebula"

    def handle(self, *args, **options):
        if not args:
            return self.handle_app(**options)
        else:
            try:
                app_list = [models.get_app(app_label) for app_label in args]
            except (ImproperlyConfigured, ImportError), e:
                raise CommandError("%s. Are you sure your INSTALLED_APPS setting is correct?" % e)
            output = []
            for app in app_list:
                app_output = self.handle_app(app, **options)
                if app_output:
                    output.append(app_output)
            return "\n".join(output)

    def handle_app(self, app=None, **options):
        quiet = options.get('quiet', False)
        for model in models.get_models(app):
            if issubclass(model, AggregatedBlog) and \
               model != AggregatedBlog and \
               callable(getattr(model.objects, 'fetch_feeds', None)):
                if not quiet:
                    print "Fetching %s.%s feeds" % (model._meta.app_label, model._meta.object_name)
                model.objects.fetch_feeds()
