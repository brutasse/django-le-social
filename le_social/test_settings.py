import os
import warnings

import django

warnings.simplefilter('always')

if django.VERSION < (1, 6):
    TEST_RUNNER = 'discover_runner.DiscoverRunner'

here = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 's3cr3t'

INSTALLED_APPS = (
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.messages',
    'le_social.registration',
    'le_social.twitter',
    'le_social.openid',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    },
}

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)

ROOT_URLCONF = ''

TEMPLATE_DIRS = (
    os.path.join(here, 'registration', 'test_templates'),
    os.path.join(here, 'openid', 'test_templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
)

SITE_ID = 1
