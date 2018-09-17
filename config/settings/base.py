"""
Django settings for MetaDeploy project.

Generated by 'django-admin startproject' using Django 1.11.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

from os import environ
from pathlib import Path
import dj_database_url
from django.core.exceptions import ImproperlyConfigured


BOOLS = ('True', 'true', 'T', 't', '1', 1)


class NoDefaultValue:
    pass


def env(name, default=NoDefaultValue, type_=str):
    """
    Get a configuration value from the environment.

    Arguments
    ---------
    name : str
        The name of the environment variable to pull from for this
        setting.
    default : any
        A default value of the return type in case the intended
        environment variable is not set. If this argument is not passed,
        the environment variable is considered to be required, and
        ``ImproperlyConfigured`` may be raised.
    type_ : callable
        A callable that takes a string and returns a value of the return
        type.

    Returns
    -------
    any
        A value of the type returned by ``type_``.

    Raises
    ------
    ImproperlyConfigured
        If there is no ``default``, and the environment variable is not
        set.
    """
    try:
        val = environ[name]
    except KeyError:
        if default == NoDefaultValue:
            raise ImproperlyConfigured(
                f'Missing environment variable: {name}.'
            )
        val = default
    val = type_(val)
    return val


# Build paths inside the project like this: str(PROJECT_ROOT / 'some_path')
PROJECT_ROOT = Path(__file__).absolute().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ']0sSXX^7>L2J9Jn(F9=oA/:&T:MRSxl^L@a~|[kYxHp;YIzF`;'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DJANGO_DEBUG', default=False, type_=lambda x: x in BOOLS)

MODE = env('DJANGO_MODE', default='dev' if DEBUG else 'prod')

ALLOWED_HOSTS = [
    '127.0.0.1',
    '127.0.0.1:8000',
    '127.0.0.1:8080',
    'localhost',
    'localhost:8000',
    'localhost:8080',
] + [
    el.strip()
    for el
    in env('DJANGO_ALLOWED_HOSTS', default='', type_=lambda x: x.split(','))
    if el.strip()
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django_extensions',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'django_rq',
    'scheduler',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'colorfield',
    'rest_framework',
    'metadeploy',
    'metadeploy.multisalesforce',
    'metadeploy.api',
    'django_js_reverse',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(PROJECT_ROOT / 'dist'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # `allauth` needs this from django:
                'django.template.context_processors.request',
                # custom
                'metadeploy.context_processors.env',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

WSGI_APPLICATION = 'metadeploy.wsgi.application'

SITE_ID = 1

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        default='postgres:///metadeploy',
    ),
}


# URL configuration:
ROOT_URLCONF = 'metadeploy.urls'

# Must end in a /, or you will experience surprises:
ADMIN_AREA_PREFIX = 'admin/'

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.MinimumLengthValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.CommonPasswordValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.NumericPasswordValidator'
        ),
    },
]

LOGIN_REDIRECT_URL = '/'


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Media files
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_ACCESS_KEY_ID = env('BUCKETEER_AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('BUCKETEER_AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('BUCKETEER_BUCKET_NAME')


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATICFILES_DIRS = [
    str(PROJECT_ROOT / 'dist'),
]
STATIC_URL = '/static/'
STATIC_ROOT = str(PROJECT_ROOT / 'staticfiles')

# if MODE == 'dev':
#     static_dir_root = 'static/dist'
# else:
#     static_dir_root = 'static/dist/min'

# Per the docs:
# > Absolute path to a directory of files which will be served at the root of
# > your application (ignored if not set).
# Set this way, this lets us serve the styleguide relative to itself. If you
# access the styleguide at `/styleguide/`, then the relative path asset
# requests it makes will land in WhiteNoise, and get served appropriately,
# given how the static directory is structured (with an internal `styleguide`
# directory).
# This comes at a cost, though:
# > you won't benefit from cache versioning
# WHITENOISE_ROOT = PROJECT_ROOT.joinpath(static_dir_root)

SOCIALACCOUNT_PROVIDERS = {
    'salesforce-production': {
        'SCOPE': ['web', 'full', 'refresh_token'],
    },
    'salesforce-test': {
        'SCOPE': ['web', 'full', 'refresh_token'],
    },
    'salesforce-custom': {
        'SCOPE': ['web', 'full', 'refresh_token'],
    },
}
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = False


JS_REVERSE_JS_VAR_NAME = 'api_urls'
JS_REVERSE_EXCLUDE_NAMESPACES = ['admin']


# Redis configuration:

REDIS_LOCATION = '{0}/{1}'.format(
    env('REDIS_URL', default='redis://localhost:6379'),
    0,
)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_LOCATION,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'IGNORE_EXCEPTIONS': True,
        },
    },
}
RQ_QUEUES = {
    'default': {
        'USE_REDIS_CACHE': 'default',
        'DEFAULT_TIMEOUT': 360,
    },
    'short': {
        'USE_REDIS_CACHE': 'default',
        'DEFAULT_TIMEOUT': 10,
    },
}


# SF Connected App and GitHub configuration:
CONNECTED_APP_CLIENT_SECRET = env('CONNECTED_APP_CLIENT_SECRET')
CONNECTED_APP_CALLBACK_URL = env('CONNECTED_APP_CALLBACK_URL')
CONNECTED_APP_CLIENT_ID = env('CONNECTED_APP_CLIENT_ID')
GITHUB_TOKEN = env('GITHUB_TOKEN')


# Raven / Sentry
SENTRY_DSN = env('SENTRY_DSN', default='')

if SENTRY_DSN:
    INSTALLED_APPS += ['raven.contrib.django.raven_compat']
    RAVEN_CONFIG = {
        'dsn': SENTRY_DSN,
    }
    MIDDLEWARE = [
        (
            'raven.contrib.django.raven_compat.middleware.'
            'SentryResponseErrorIdMiddleware'
        ),
    ] + MIDDLEWARE

    if not DEBUG:
        LOGGING = {
            'version': 1,
            'disable_existing_loggers': True,
            'root': {
                'level': 'WARNING',
                'handlers': ['sentry'],
            },
            'formatters': {
                'verbose': {
                    'format': (
                        '%(levelname)s %(asctime)s %(module)s %(process)d '
                        '%(thread)d %(message)s'
                    ),
                },
                "rq_console": {
                    "format": "%(asctime)s %(message)s",
                    "datefmt": "%H:%M:%S",
                },
            },
            'handlers': {
                'sentry': {
                    'level': 'ERROR',
                    'class': (
                        'raven.contrib.django.raven_compat.handlers.'
                        'SentryHandler'
                    ),
                    'tags': {'custom-tag': 'x'},
                },
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'verbose'
                },
                "rq_console": {
                    "level": "DEBUG",
                    "class": "rq.utils.ColorizingStreamHandler",
                    "formatter": "rq_console",
                    "exclude": ["%(asctime)s"],
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
                "rq.worker": {
                    "handlers": ["rq_console", "sentry"],
                    "level": "DEBUG"
                },
            },
        }
