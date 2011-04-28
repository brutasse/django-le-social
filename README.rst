Django-le-social
================

Django-le-social is an external registration helper for Django. It currently
lets you use Twitter (OAuth) and OpenID authentication.

It's more a framework than a drop-in app in the sense that it won't create any
user data for you: when a user comes from an external authentication source,
django-le-social executes a method that you decide. There is no user creation,
no new model instance, no user login. You need to decide what to do, mainly
store the OAuth token or the OpenID data and log the user in.

* Author: Bruno Renié
* Licence: BSD
* Compatibility: Django 1.3+ (class-based-views required)
* Requirements: tweepy, python-openid
* Documentation: http://django-le-social.readthedocs.org/en/latest/
