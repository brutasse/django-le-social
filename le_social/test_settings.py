import os
import warnings

warnings.simplefilter('always')

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

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)
MIDDLEWARE_CLASSES = MIDDLEWARE  # Django < 1.10

ROOT_URLCONF = 'le_social.registration.tests.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [
        os.path.join(here, 'registration', 'test_templates'),
        os.path.join(here, 'openid', 'test_templates'),
    ],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

SITE_ID = 1
