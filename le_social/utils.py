"""
Helper that tries to import the class-based-views API from django and
fallback to the django-cbv package.
"""
from django import VERSION
from django.core.urlresolvers import reverse
from django.utils.functional import lazy

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
