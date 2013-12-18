# -*- coding: utf-8 -*-

# Django settings for calebasse project.

import os
from logging.handlers import SysLogHandler

PROJECT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'calebasse')

DEBUG = True
TEMPLATE_DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(PROJECT_PATH, 'calebasse.sqlite3'),                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr-fr'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True
FORMAT_MODULE_PATH = 'calebasse.formats'

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(os.path.join(PROJECT_PATH, '..'), 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ct(a@ny^_)8v-^)jkdzbktqg6ajfn6y!zdjum^(f_o!h0jeotq'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'calebasse.middleware.request.GlobalRequestMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'reversion.middleware.RevisionMiddleware',
    # Entr'ouvert wsgi middleware to expose version
    'entrouvert.djommon.middleware.VersionMiddleware',
)

ROOT_URLCONF = 'calebasse.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'calebasse.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, "templates")
)

TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages")

FIXTURE_DIRS = (
        os.path.join(PROJECT_PATH, 'fixtures'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'reversion',
    'south',
    'django.contrib.admin',
    'ajax_select',
    #'debug_toolbar',
    'widget_tweaks',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'calebasse.agenda',
    'calebasse.dossiers',
    'calebasse.actes',
    'calebasse.facturation',
    'calebasse.personnes',
    'calebasse.ressources',
    'calebasse.statistics',
    'calebasse.middleware.request',
    'south',
    'raven.contrib.django.raven_compat'
)

INTERNAL_IPS=('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
    },
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)-8s %(name)s.%(message)s',
            'datefmt': '%Y-%m-%d %a %H:%M:%S'
        },
        'syslog': {
            'format': 'calebasse (pid=%(process)d) %(levelname)s %(name)s: %(message)s',
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'syslog': {
            'level': 'DEBUG',
            'class': 'entrouvert.logging.handlers.SysLogHandler',
            'formatter': 'syslog',
            'facility': SysLogHandler.LOG_LOCAL0,
            'address': '/dev/log',
            'max_length': 999,
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        '': {
            'handlers': ['sentry', 'syslog'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        }
    },
}

# AJAX Select
AJAX_LOOKUP_CHANNELS = {
    #   pass a dict with the model and the field to search against
    'worker' : ('calebasse.personnes.lookup', 'WorkerLookup'),
    'intervenant' : ('calebasse.personnes.lookup', 'IntervenantLookup'),
    #'patientrecord'  : {'model':'dossiers.PatientRecord', 'search_field':'display_name'}
    #'coordinators'  : {'model':'dossiers.PatientRecord', 'search_field':'display_name'}
    'patientrecord' : ('calebasse.dossiers.lookups', 'PatientRecordLookup'),
    'school' : {'model':'ressources.School', 'search_field':'name'},
    'addresses' : ('calebasse.dossiers.lookups', 'PatientAddressLookup'),
    'worker-or-group' : ('calebasse.ressources.lookups', 'WorkerOrGroupLookup'),
}

# Default URL after login
LOGIN_REDIRECT_URL = '/'

# Sentry / raven configuration
# You need to overload this option in the local_settings.py
RAVEN_CONFIG = {}

# Base directory for generated patient files
PATIENT_FILES_BASE_DIRECTORY = None

# Client side base directory for generated patient files
CLIENT_SIDE_PATIENT_FILES_BASE_DIRECTORY =  None

# Patient subdirectories
PATIENT_SUBDIRECTORIES = (
    u'Assistante sociale',
    u'Consultation',
    u'Courriers',
    u'Demande',
    u'Demandes prises en charge',
    u'Educateur spécialisé',
    u'Ergothérapie',
    u'Groupe',
    u'Kinésithérapie',
    u'Logico-mathématiques',
    u'Neuro-psychologie',
    u'Orientation',
    u'Orthophonie',
    u'Psychologie',
    u'Psychomotricité',
    u'Psychopédagogue',
    u'Synthèses',
    u'TCC',
)

# RTF templates directory
RTF_TEMPLATES_DIRECTORY = None
# Use patient home dictrory for RTF files generated
# PATIENT_FILES_BASE_DIRECTORY must be set to work
USE_PATIENT_FILE_RTF_REPOSITORY_DIRECTORY = False
# RTF files generated directory
RTF_REPOSITORY_DIRECTORY = None

# Invoicing file saving directory
INVOICING_DIRECTORY = None

#CSV_ENCODING = 'cp1252' #For windows : windows-1252/Winlatin1
#CSVPROFILE = {\
#    'delimiter' : ';',
#    'quotechar' : '"',
#    'doublequote' : True
#    'skipinitialspace' : False
#    'lineterminator' : '\r\n'
#    'quoting' : csv.QUOTE_MINIMAL
#}

# IRIS/B2 transmission
# B2_TRANSMISSION = {
#    'output_directory': '/var/lib/calebasse/B2/',
#    # B2 informations
#    'nom': 'CMPP FOOBAR',                      # mandatory
#    'numero_emetteur': '123456789',            # mandatory
#    'norme': 'CP  ',
#    'type_emetteur': 'TE',
#    'application': 'TR',
#    'categorie': '189',
#    'statut': '60',
#    'mode_tarif': '05',
#    'message': 'ENTROUVERT 0143350135 CALEBASSE 1307',
#    # SMTP configuration
#    'smtp_from': 'transmission@domain.net',    # mandatory
#    'smtp_host': '127.0.0.1',
#    'smtp_port': 25,
#    'smtp_login': '',
#    'smtp_password': '',
#    # delay between two mails, in seconds, or None
#    'smtp_delay': None,
# }

try:
    from local_settings import *
except ImportError:
    print """ 
    -------------------------------------------------------------------------
    You need to create a local_settings.py file which needs to contain at least
    database connection information.
    
    Copy local_settings_example.py to local_settings.py and edit it.
    -------------------------------------------------------------------------
    """
    import sys 
    sys.exit(1)

