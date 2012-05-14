#!/usr/bin/env python
import os
import sys

import django

from django.conf import settings
try:
    from django.utils.functional import empty
except ImportError:
    empty = None

from le_social import openid, registration




def test_templates(module):
    return os.path.join(os.path.dirname(module.__file__), 'test_templates')


def setup_test_environment():
    # reset settings
    settings._wrapped = empty

    apps = [
        'django.contrib.sessions',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sites',
        'django.contrib.messages',

        'le_social.twitter',
        'le_social.openid',
        'le_social.registration',
    ]

    middleware_classes = [
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
    ]

    context_processors = [
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]

    if django.VERSION[:2] <= (1, 2):
        middleware_classes.append('cbv.middleware.DeferredRenderingMiddleware')
        apps.append('django.contrib.admin')

    settings_dict = {
        "DATABASES": {
            'default': {
                'ENGINE': "django.db.backends.sqlite3",
                'NAME': 'le_social.sqlite',
            },
        },
        "ROOT_URLCONF": "",
        "MIDDLEWARE_CLASSES": middleware_classes,
        "INSTALLED_APPS": apps,
        "TEMPLATE_DIRS": [
            test_templates(openid),
            test_templates(registration),
        ],
        "TEMPLATE_CONTEXT_PROCESSORS": context_processors,
        "SITE_ID": 1,
    }

    # set up settings for running tests for all apps
    settings.configure(**settings_dict)


def runtests(*test_args):
    if not test_args:
        test_args = ('twitter', 'openid', 'registration')
    setup_test_environment()

    parent = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, parent)
    try:
        from django.test.simple import DjangoTestSuiteRunner

        def run_tests(test_args, verbosity, interactive):
            runner = DjangoTestSuiteRunner(
                verbosity=verbosity, interactive=interactive, failfast=False)
            return runner.run_tests(test_args)
    except ImportError:
        # for Django versions that don't have DjangoTestSuiteRunner
        from django.test.simple import run_tests
    failures = run_tests(test_args, verbosity=1, interactive=True)
    sys.exit(failures)


if __name__ == '__main__':
    runtests()
