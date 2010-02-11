# Django settings for myproject project.
import os 
import logging
import sys

gettext = lambda s: s

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Kaitlin Lee', 'kaitlin@hollabackdc.org'),
)
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

BLOG_URLCONF_ROOT = 'apps.blog.urls'
URL_ROOT_HANDLER = 'apps.blog.views.process_root_request'

sys.path.insert(0, os.path.join(PROJECT_ROOT, 'apps'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'compat'))

from lib.threadlocals import SiteIDHook

MANAGERS = ADMINS

DATABASE_ENGINE = ''           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = ''             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

EMAIL_HOST = 'smtp.webfaction.com'
EMAIL_HOST_USER = 'kaitlin_hbdc'
EMAIL_HOST_PASSWORD = 'ae5e80bd'
DEFAULT_FROM_EMAIL = 'server@hollabackdc.kaitlinlee.com'
SERVER_EMAIL = 'server@hollabackdc.kaitlinlee.com'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = SiteIDHook()

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
STATIC_URL = '/media/'

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'o*_rucsbk%f19*)@03u*suj45rk*-y05=zu8-lli^c0g@%o$c^'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'lib.template_loaders.get_theme_template',
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)
ROOT_URLCONF = 'urls'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'middleware.dynamicsite.DynamicSiteMiddleware', # before feedburner
    'middleware.feedburner.FeedburnerMiddleware',
    'middleware.url.UrlMiddleware',
    'lib.threadlocals.ThreadLocalsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'maintenancemode.middleware.MaintenanceModeMiddleware',
    'middleware.redirect.RedirectMiddleware',
    'openidconsumer.middleware.OpenIDMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'middleware.ajax_errors.AjaxMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'pingback.middleware.PingbackMiddleware',
)
TEMPLATE_CONTEXT_PROCESSORS =(
    'django.core.context_processors.request',
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'cms.context_processors.media',
    "context_processors.settings_vars",
    )

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'accounts.backends.CommentApprovingBackend',
    'accounts.backends.EmailBackend',
    'openidconsumer.backend.OpenidBackend',
)

LANGUAGES = (
    ('en', gettext('English')),
    )
LANGUAGE_CODE = 'en'

CAPTCHA = 'recaptcha'
RECAPTCHA = {'hollabackdc.kaitlinlee.com': {'public': '6LdQsAoAAAAAAOBzjZfSBLGQu_r0hDVAqgfz70UU', 'private': '6LdQsAoAAAAAALC5fLqiw66zGoDOxeNCpRP1jS3R' }}

BLOG_NAME = 'HollaBackDC'

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
    'django.contrib.comments',
    'django.contrib.sites',
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
#    'south',
    'django.contrib.sitemaps',
    'django.contrib.flatpages',
    'django.contrib.markup',
    'lib',
    'pytils',
    'accounts',
    'blog',
    'discussion',
    'tagging',
    'typogrify',
    'render',
    'postimage',
    'openidconsumer',
    'openidserver',
    'revcanonical',
    'pingback',
    'watchlist',
    'robots',
    'wpimport',
    'textblocks',
    'django_extensions',
    'util'
)

APPEND_SLASH = True
REMOVE_WWW = True
SITE_PROTOCOL = 'http'
THEME = 'default'

# App settings
PAGINATE_BY = 10
NAME_LENGTH = 256
DATE_FORMAT = "m.j.Y"
TIME_FORMAT = "G:i"
ACTION_RECORD_DAYS = 3
# Set to integer value to close comments after this number of days
COMMENTS_EXPIRE_DAYS = None
# Set to True to disable rel="nofollow" in comments
COMMENTS_FOLLOW = False

# OpenID
OPENID_WITH_AUTH = True
OPENID_REDIRECT_NEXT = '/'

# Pingback
PINGBACK_SERVER = {
    'post_detail': 'pingback.getters.post_get',
    }
PINGBACK_RESPONSE_LENGTH = 200

# TODO: move this list to DB
DIRECTORY_URLS = (
    'http://www.google.com/webmasters/tools/ping',
    'http://ping.blogs.yandex.ru/RPC2',
    'http://rpc.technorati.com/rpc/ping',
    )

# Default markup language for you posts. Choices are bbcode, text, html, markdown
RENDER_METHOD = 'html'

# Gravatar options
GRAVATAR_ENABLE = False
DEFAULT_AVATAR_IMG = 'avatar.jpg'
DEFAULT_AVATAR_SIZE = 80
DEFAULT_AVATAR_PATH = MEDIA_URL + 'avatars/'

#if "false" robots application would not use auto-generated sitemap.xml
ROBOTS_USE_SITEMAP = True

APPEND_MTIME_TO_STATIC = True # Modification time will be appended in media_css and media_js templatetags
WYSIWYG_ENABLE = False # WYSIWYG for post text in admin
ANONYMOUS_COMMENTS_APPROVED = False # Do anonymous comments become autoapproved?
DEBUG_SQL = False # Show debug information about sql queries at the bottom of page
SHORT_POSTS_IN_FEED = False # Show full post in feed
USE_ATOM = True # Atom is standard, so we're using it by default
FEEDBURNER = {} # Feedburner disabled by default

# Postimage settings
POSTIMAGE_ROOT = MEDIA_ROOT
POSTIMAGE_URL = MEDIA_URL

STATIC_PAGES = (
    # Name, url, title. When bool(name) is False, separator will be inserted
    ('Blog', 'blog', 'HollaBackDC Blog'),
    )

SOCIAL_BOOKMARKS = ('delicious', 'reddit', 'slashdot', 'digg', 'technorati', 'google')

THEMES_DIR = os.path.join(PROJECT_ROOT, "themes") # Byteflow themes. Your themes can be out of PROJECT_ROOT.

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

if not hasattr(globals(), 'THEME_STATIC_ROOT'):
   THEME_STATIC_ROOT = os.path.join(STATIC_ROOT, THEME + '/')

if not hasattr(globals(), 'THEME_STATIC_URL'):
   THEME_STATIC_URL = os.path.join(STATIC_URL, THEME + '/')
