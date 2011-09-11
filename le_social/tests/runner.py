#! /usr/bin/env python
import optparse
import sys

from django.conf import settings
from django.core.management import call_command
try:
    from django.utils.functional import empty
except ImportError:
    empty = None


APPS = (
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.contenttypes',

    'le_social.twitter',
    'le_social.openid',
    'le_social.registration',
    'le_social.tests',  # For test templates
)


def setup_test_environment():
    # reset settings
    settings._wrapped = empty

    # set up settings for running tests for all apps
    settings.configure(**{
        "DATABASES": {
            'default': {
                'ENGINE': "django.db.backends.sqlite3",
                'NAME': 'le_social.sqlite',
            },
        },
        "SITE_ID": 1,
        "ROOT_URLCONF": "",
        "STATIC_URL": "/static/",
        "MIDDLEWARE_CLASSES": [
            "django.middleware.common.CommonMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            'django.middleware.csrf.CsrfViewMiddleware',
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ],
        "INSTALLED_APPS": APPS,
        "TEMPLATE_DIRS": [],
    })


def main():
    usage = "%prog [options] [app app app]"
    parser = optparse.OptionParser(usage=usage)

    parser.add_option("-v", "--verbosity",
        action="store",
        dest="verbosity",
        default="1",
        type="choice",
        choices=["0", "1", "2"],
        help="verbosity; 0=minimal output, 1=normal output, 2=all output",
    )
    parser.add_option("--coverage",
        action="store_true",
        dest="coverage",
        default=False,
        help="hook in coverage during test suite run and save out results",
    )

    options, args = parser.parse_args()

    if options.coverage:
        try:
            import coverage
        except ImportError:
            sys.stderr.write("coverage is not installed.\n")
            sys.exit(1)
        else:
            cov = coverage.coverage(auto_data=True)
            cov.start()
    else:
        cov = None

    setup_test_environment()

    call_command("test", verbosity=int(options.verbosity), *args)

    if cov:
        cov.stop()
        cov.save()


if __name__ == "__main__":
    main()
