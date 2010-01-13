# -*- mode: python; coding: utf-8; -*-

import os

import django
from django.core.management.base import LabelCommand, CommandError

CONFIG = {

'nginx':
    '''
    location /static {
        alias %(cwd)s/static;
        expires 1M;
        add_header last-modified "";
    }
    location /media {
        alias %(cwd)s/media;
        expires 1M;
        add_header last-modified "";
    }
    location /admin-media {
        alias %(django)s/contrib/admin/media;
        expires 1M;
        add_header last-modified "";
    }
''',

'apache':
    '''
    Alias /media/       %(cwd)s/media/
    <Location /media/>
        SetHandler None
        ExpiresDefault "access plus 1 month"
    </Location>
    Alias /static/      %(cwd)s/static/
    <Location /static/>
        SetHandler None
        ExpiresDefault "access plus 1 month"
    </Location>
    Alias /admin-media/ %(django)s/contrib/admin/media/
    <Location /admin-media/>
        SetHandler None
        ExpiresDefault "access plus 1 month"
    </Location>
'''
}

class Command(LabelCommand):
    help = u'Output webserver rules to config static directories'
    args = '|'.join(CONFIG)

    def handle_label(self, label, **opts):
        if label not in CONFIG:
            raise CommandError('We support only %s' % ', '.join(CONFIG))
        pats = {'django': os.path.dirname(django.__file__),
                'cwd': os.getcwd()}
        return CONFIG[label] % pats
