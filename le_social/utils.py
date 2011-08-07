"""
Helper that tries to import the class-based-views API from django and
fallback to the django-cbv package.
"""
import random

from django import VERSION
from django.core.urlresolvers import reverse
from django.utils.functional import lazy
from django.utils.hashcompat import sha_constructor

if VERSION >= (1, 3):
    from django.views import generic
else:
    try:
        import cbv as generic
    except ImportError:
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured("Either Django>=1.3 or the django-cbv "
                                   "package is required.")

reverse_lazy = lazy(reverse, str)


def make_activation_key(derive_from):
    """
    Generate a random / salted activation key from a base
    string (a username for instance).
    """
    salt = sha_constructor(str(random.random())).hexdigest()[:5]
    if isinstance(derive_from, unicode):
        derive_from = derive_from.encode('utf-8')
    return sha_constructor(salt + derive_from).hexdigest()
