# Django settings for bee project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'
#DATABASE_NAME   = '/home/adammck/Projects/Unicef/yjir/frontend/bee/dev.sqlite'
DATABASE_NAME   = '/home/adam/yjir2/frontend/bee/dev.sqlite'

# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = 'America/New_York'

# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'cvpug#wllu_@s9_63=s4mt6(e8er3j3r2jf%ybmdoy&rkwj1up'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    #'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    #'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
	#'bee.middleware.MobiledMiddleware',
    #'django.middleware.common.CommonMiddleware',
    #'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'bee.urls'

#TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
#)

INSTALLED_APPS = (
    #'django.contrib.auth',
    #'django.contrib.contenttypes',
    #'django.contrib.sessions',
    #'django.contrib.sites',
    'bee.yjir'
)




# MOBILED CONFIGURATION
# =====================
MOBILED_UDP_PORT = 4000 # for resource discovery and p2p

# KANNEL CONFIGURATION
# ====================
KANNEL_SERVER       = "127.0.0.1"
KANNEL_PORT_RECEIVE = 4500  # kannel (outgoing sms) port
KANNEL_PORT_SEND    = 13013 # mobiled (incomming sms) port
KANNEL_EXEC         = "/cgi-bin/sendsms" # path to executable for sending sms messages
KANNEL_USERNAME     = "mobiled"
KANNEL_PASSWORD     = "mobiled"

# ASTERISK CONFIG
# ===============
ASTERISK_SERVER          = "127.0.0.1"
ASTERISK_MANAPI_PORT     = 5038 # management api port
ASTERISK_MANAPI_USERNAME = "yjir"
ASTERISK_MANAPI_PASSWORD = "yjir"
ASTERISK_FASTAGI_PORT    = 6500 # 
ASTERISK_CHANNELS        = ["Zap/1"]
ASTERISK_DEFAULT_TTS     = "swift"

# EMAIL CONFIGURATION
# ===================
EMAIL_SERVER  = "localhost"
EMAIL_FROM    = "no-reply@unicef.org"
EMAIL_SUBJECT = "Message from YJIR"

# OTHER STUFF
# ===========
TEST_NUMBER = "16464105122" # chris
NO_ACTIONS_REPLY = "YJIR Error: Invalid Scope (%s) + Keyword (%s)"

