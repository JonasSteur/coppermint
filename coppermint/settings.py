from os import path
from environ import Path, Env


# Django-environ basics
root = Path(__file__) - 2
env = Env(DEBUG=(bool, False),)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = path.dirname(path.dirname(path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ce3l$!cms25%5-mz8idbw^-bgz2(b)%&&0951=0vw9xpfuv%%t'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Whitenoise to handle static
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'coppermint.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'coppermint.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = env('STATIC_ROOT', default=root('static'))
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        # Start logging at INFO level, specify stricter levels further in handlers and loggers
        'level': env('LOG_LEVEL', default='INFO'),
        'handlers': [ 'console'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            # Eat all log messages with this handler
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            # Sent everything to the console
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        # DisallowedHost errors happen early, we need to catch those separately
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
        # ignore django request warnings for e.g. 404 and 429
        'django.request': {
            'level': 'WARNING',
            'handlers': ['null'],
            'propagate': False,
        },
        # If something happens while logging an error, we want to log it via another way, so Raven and Sentry errors go
        # to the console.
        'coppermint': {
            'level': env('LOG_LEVEL_COPPERMINT', default='INFO'),
            'handlers': ['console'],
            'propagate': env.bool('LOGGERS_COPPERMINT_PROPAGATE', default=False),  # Testing override
        },
        'celery': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': True,
        },
    },
}


# Celery (task queue) settings
# Do mind every celery setting must have the prefix CELERY_
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_ALWAYS_EAGER = env.bool('CELERY_ALWAYS_EAGER', True)
CELERY_BROKER_TRANSPORT_OPTIONS = env('CELERY_BROKER_TRANSPORT_OPTIONS',
                                      default={'visibility_timeout': 1800},
                                      cast={'value': str, 'cast': {'visibility_timeout': int}}, )
CELERY_BROKER_CONNECTION_MAX_RETRIES = 5
# https://docs.celeryproject.org/en/latest/userguide/configuration.html#broker-pool-limit
# This setting has been added to test if it solves the 'ConnectionError' that happens occasionally
# TODO https://vikingco.atlassian.net/browse/INT-5363
CELERY_BROKER_POOL_LIMIT = None
CELERY_WORKER_HIJACK_ROOT_LOGGER = False
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_ACKS_LATE = env('CELERY_TASK_ACKS_LATE', default=True)

CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_EXCHANGE = 'default'
CELERY_DEFAULT_ROUTING_KEY = 'default'
CELERY_SEND_TASK_ERROR_EMAILS = False
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TRACK_STARTED = True
CELERY_ROUTES = {}
CELERY_QUEUES = {}
CELERY_TIMEZONE = 'Europe/Brussels'

# The definition of the periodic tasks initiated by celery-beat
CELERY_BEAT_SCHEDULE = {
}
