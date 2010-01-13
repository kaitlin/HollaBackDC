# -*- mode: python; coding: utf-8; -*-

from django.conf import settings


class ApplicationChecker(object):
    "Checks if application is enabled"
    def __getattr__(self, attr):
        return attr in settings.INSTALLED_APPS
appcheck = ApplicationChecker()
