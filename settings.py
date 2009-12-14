# Django settings for myproject project.
import os 
import logging

gettext = lambda s: s

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Kaitlin Lee', 'kaitlin@hollabackdc.org'),
)
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

MANAGERS = ADMINS

DATABASE_ENGINE = ''           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = ''             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media') 

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'o*_rucsbk%f19*)@03u*suj45rk*-y05=zu8-lli^c0g@%o$c^'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)
ROOT_URLCONF = 'urls'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
)
TEMPLATE_CONTEXT_PROCESSORS =(
    'django.core.context_processors.request',
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'cms.context_processors.media',
    )

LANGUAGES = (
    ('en', gettext('English')),
    )
LANGUAGE_CODE = 'en'

CMS_DEFAULT_LANGUAGE = 'en'

CMS_TEMPLATES = (
    ('generic.html', gettext('default')),
    )
#CMS_PLACEHOLDER_CONF = {
#    'content': {
#        'plugins': ('TextPlugin', 'PicturePlugin'),
#        'extra_context': {'theme': 'wide' },
#        'name': gettext('Content')
#    },
#    'right-column': {
#        "plugins": ('TeaserPlugin', 'PicturePlugin'),
#        "extra_context": {'theme':'small'},
#        "name": gettext("Right Column")
#    }
#}
TEMPLATE_DIRS = (
#    "/home/kaitlin/webapps/hollabackdc/hbdcsite/templates",
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'hbdc',
    'cms',
    'cms.plugins.text',
    'cms.plugins.picture',
    'cms.plugins.link',
    'cms.plugins.file',
    'cms.plugins.snippet',
    'cms.plugins.googlemap',
    'mptt',
    'publisher',
    'reversion',
    'cms.plugins.twitter',
    'cms.plugins.flash',
    'cms.plugins.teaser',
)

try:
    from local_settings import *
except ImportError, exp:
    pass
if DEBUG:
    logging.getLogger().setLevel(logging.DEBUG)
    try:
        import test_utils
        INSTALLED_APPS += ('test_utils',)
    except ImportError:
        logging.warning("django-test-utils is not installed; URL crawler will not be available")
    
    try:
        import debug_toolbar
        MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware', )
        INSTALLED_APPS += ('debug_toolbar',)
        DEBUG_TOOLBAR_CONFIG = {
            'INTERCEPT_REDIRECTS': False,
            'HIDE_DJANGO_SQL': True,
        }
    except ImportError:
        logging.warning("Unable to import debug_toolbar - continuing without it. Try `pip install django-debug-toolbar`")
