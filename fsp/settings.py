import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-stdwqr7b$-wj5smck0n^lf*mcgr(f&x(_w2(7qpg6vr8w%3@4)'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'fields.apps.FieldsConfig',
    'users.apps.UsersConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'fsp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'fsp.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'flds',
        'USER' : 'py_user',
        'PASSWORD' : 'py123',
        'HOST' : '127.0.0.1',
        'PORT' : '5432',
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'user_warning': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'log/user_warning.log',
        },
        'user_info': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'log/user_info.log',
        },
        'field_warning': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'log/field_warning.log',
        },
        'field_info': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'log/field_info.log',
        },

    },
    'loggers': {
        'users.views': {
            'handlers': ['user_info'],
            'level': 'INFO',
            'propagate': True,
        },
        'users.forms': {
            'handlers': ['user_info', 'user_warning'],
            'level': 'INFO',
            'propagate': True,
        },
        'fields.forms': {
            'handlers': ['field_info', 'field_warning'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_DIR = BASE_DIR / 'static'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_DIRS = [(os.path.join(BASE_DIR,'static'))]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'