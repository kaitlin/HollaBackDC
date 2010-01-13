# -*- mode: python; coding: utf-8; -*-

import re
import sys

from django.contrib.sites import models as site_app

from lib.helpers import signals

RE_VALID_DOMAIN = re.compile(r'([A-Z0-9]([A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}')

@signals.post_syncdb(sender=site_app)
def create_site_interactively(app, created_models, verbosity, **kwargs):
    from django.contrib.sites.models import Site
    domain, name = 'example.com', 'example'
    if Site in created_models:
        if kwargs.get('interactive', True):
            domain, name = get_site_interactive(domain, name)
            try:
                site = Site.objects.all()[0]
                site.domain = domain
                site.name = name
                site.save()
            except IndexError:
                pass
        if not Site.objects.count():
            Site.objects.create(domain=domain, name=name)
    Site.objects.clear_cache()


def get_site_interactive(def_domain=None, def_name=None):
    msg = "\nYou have just initialized your sites subsystem, which " \
        "means you don't have any \nsites defined. Please enter domain and " \
        "name of your site (you can create more \nin admin interface later)"
    print msg
    domain, name = None, None
    while not domain:
        input_msg = 'Domain'
        if def_domain:
            input_msg += ' (Leave blank to use %r)' % def_domain
        domain = raw_input(input_msg + ': ')
        if def_domain and not domain:
            domain = def_domain
        if not RE_VALID_DOMAIN.match(domain.upper()):
            sys.stderr.write("Error: this domain is invalid")
            domain = None
    while not name:
        input_msg = 'Name'
        if def_name:
            input_msg += ' (Leave blank to use %r)' % def_name
        name = raw_input(input_msg + ': ')
        if def_name and not name:
            name = def_name
    return domain, name


@signals.post_syncdb(sender=site_app)
def create_about_page(app, created_models, verbosity, **kwargs):
    from django.contrib.flatpages.models import FlatPage
    from django.contrib.sites.models import Site
    if FlatPage not in created_models:
        return
    if FlatPage.objects.count():
        return
    text = '''Hello, I'm default about page.

Please change me in admin. I'm also known as FlatPage.'''
    about = FlatPage(url='/about/', title='About', content=text,
                     enable_comments=False, registration_required=False)
    about.save()
    about.sites.add(*Site.objects.all())
