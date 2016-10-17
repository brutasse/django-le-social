try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django.http import HttpResponse

from .. import views


class Common(object):
    """
    Stuff shared by the two views.
    """
    def get_return_url(self):
        return reverse('openid_callback')

    def failure(self, message):
        return HttpResponse(message)


class Begin(Common, views.Begin):
    template_name = 'le_social/openid/openid.html'
begin = Begin.as_view()


class Callback(Common, views.Callback):
    def success(self):
        openid_url = self.openid_response.identity_url
        return HttpResponse('OpenID association: %s' % openid_url)
callback = Callback.as_view()
