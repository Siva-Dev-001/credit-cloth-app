"""
Django settings for skdresses project.

Generated by 'django-admin startproject' using Django 5.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

import os, random, string
from pathlib import Path
from dotenv import load_dotenv
from django.utils.translation import gettext_lazy as _
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-+5+o$y7a=s8gi9r8((b#sbdk*6b469atwet)$pyqe=-130zkir'
# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = os.environ.get('SECRET_KEY')
# if not SECRET_KEY:
#     SECRET_KEY = ''.join(random.choice( string.ascii_lowercase  ) for i in range( 32 ))
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['13.126.22.62','localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'retailapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'skdresses.urls'

HOME_TEMPLATES = os.path.join(BASE_DIR, 'templates')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [HOME_TEMPLATES],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'skdresses.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DB_ENGINE   = os.getenv('DB_ENGINE'   , None)
DB_USERNAME = os.getenv('DB_USERNAME' , None)
DB_PASS     = os.getenv('DB_PASS'     , None)
DB_HOST     = os.getenv('DB_HOST'     , None)
DB_PORT     = os.getenv('DB_PORT'     , None)
DB_NAME     = os.getenv('DB_NAME'     , None)

# if DB_ENGINE and DB_NAME and DB_USERNAME:
DATABASES = { 
    'default': {
    'ENGINE'  : 'django.db.backends.' + DB_ENGINE, 
    'NAME'    : DB_NAME,
    'USER'    : DB_USERNAME,
    'PASSWORD': DB_PASS,
    'HOST'    : DB_HOST,
    'PORT'    : DB_PORT,
    }, 
}
# else:
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': 'db.sqlite3',
#         }
#     }



# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


LANGUAGES = [
    ('en', 'English'),
    ('ta', 'Tamil'),
    ('te', 'Telugu'),
    ('kn', 'Kannada'),
    ('ml', 'Malayalam'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Ensure you configure AUTH_USER_MODEL to use `CustomUser`:
# AUTH_USER_MODEL = 'retailapp.user'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'

from django.contrib import messages

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-dark',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'django-debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}


AWS_ACCESS_KEY_ID = os.getenv('AWS_KEY_ID' , None)
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_KEY' , None)
AWS_REGION = 'ap-south-1'