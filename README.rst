Django-le-social
================

.. image:: https://api.travis-ci.org/brutasse/django-le-social.svg?branch=master
   :alt: Build Status
   :target: https://travis-ci.org/brutasse/django-le-social

Django-le-social is an external registration helper for Django. It currently
lets you use Twitter (OAuth) and OpenID authentication, as well as traditional
registration.

It's more a framework than a drop-in app in the sense that it won't create
any user data for you: when a user comes from an external authentication
source, django-le-social executes a method that **you** decide. There is no
user creation, no new model instance, no user login. You need to decide what
to do, mainly store the OAuth token or the OpenID data, create a user and log
him in.


* Authors: Bruno Renié and `contributors`_
* Licence: BSD
* Compatibility: Django 1.8+
* Optional requirements: twitter, python-openid
* Documentation: https://django-le-social.readthedocs.io/en/latest/

.. _contributors: https://github.com/brutasse/django-le-social/contributors

Hacking
-------

Setup your environment::

    git clone https://brutasse@github.com/brutasse/django-le-social.git
    cd django-le-social
    mkvirtualenv --python le-social
    pip install tox

Hack, and run the tests::

    tox

`Tox`_ runs all tests on python 2.7 and 3.4 and above, as well as all the
supported Django versions.

.. _Tox: https://tox.readthedocs.io
