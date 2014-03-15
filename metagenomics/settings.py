"""
Django settings for metagenomics project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '+&j+f^vg!w7ijq3f4$g5_jlg^+tqiqp^pk)@-=^-xkd135t#ji'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

# default place for templates (Kathy)
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'mainsite/templates')]

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    # tell Django to look in subdirectories in the templates directory (Kathy)
    'django.template.loaders.app_directories.Loader',
)

ALLOWED_HOSTS = []

LOGIN_URL = '/login/'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'mainsite',
    'django.contrib.staticfiles', # added by Kathy for css
    'reversion',  #app that allows tracking of database changes
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'metagenomics.urls'

WSGI_APPLICATION = 'metagenomics.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'metagenomics',          
        'USER': 'root',            
        'PASSWORD': '123qwe',       # NEED TO SECURE THIS
        'HOST': '',                 # Set to empty string for localhost.
        'PORT': '',                 # Set to empty string for default.
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_URL = '/static/'

# For uploaded files
MEDIA_ROOT = '/media/'
MEDIA_URL = '/media/'