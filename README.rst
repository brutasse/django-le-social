Django-le-social
================

Django-le-social is an external registration helper for Django. It currently
lets you use Twitter (OAuth) and OpenID authentication, as well as traditional
registration.

It's more a framework than a drop-in app in the sense that it won't create
any user data for you: when a user comes from an external authentication
source, django-le-social executes a method that **you** decide. There is no
user creation, no new model instance, no user login. You need to decide what
to do, mainly store the OAuth token or the OpenID data, create a user and log
him in.


* Authors: see AUTHORS
* Licence: BSD
* Compatibility: Django 1.3 or Django < 1.3 + django-cbv
* Requirements: twitter, python-openid, itsdangerous
* Documentation: http://django-le-social.readthedocs.org/en/latest/

Hacking
-------

Setup your environment::

    git clone https://brutasse@github.com/brutasse/django-le-social.git
    cd django-le-social
    mkvirtualenv --python python2 le-social
    add2virtualenv .
    pip install -r requirements.txt

Hack, and run the tests::

    python setup.py test

Or do it with `Tox`_ to test on python2.6 and 2.7, as well as all the
supported Django versions::

    tox

.. _Tox: http://codespeak.net/~hpk/tox
