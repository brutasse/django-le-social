try:
    from openid.consumer.consumer import (Consumer, SUCCESS, CANCEL, FAILURE,
                                          SETUP_NEEDED)
    from openid.consumer.discover import DiscoveryFailure
    from openid.extensions import sreg, ax
except ImportError:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured(
        "python-openid is required to use le_social.openid"
    )

from django.shortcuts import redirect
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from .forms import OpenIDForm
from .middleware import OpenIDMiddleware
from .store import DjangoOpenIDStore
from .utils import get_url_host, discover_extensions, from_openid_response


class ReturnUrlMixin(object):
    return_url = None

    def get_return_url(self):
        if self.return_url is None:
            raise NotImplementedError("Either set the return_url or "
                                      "implement get_return_url()")
        return get_url_host(self.request) + self.return_url


class Begin(generic.FormView, ReturnUrlMixin):
    form_class = OpenIDForm
    sreg_attrs = {}
    ax_attrs = []
    store_class = DjangoOpenIDStore
    trust_root = '/'

    def form_valid(self, form):
        openid_url = form.cleaned_data['openid_url']
        return_url = self.get_return_url()
        return self.ask_openid(openid_url, return_url)

    def get_trust_root(self):
        return get_url_host(self.request) + self.trust_root

    def get_sreg_attrs(self):
        return self.sreg_attrs

    def get_ax_attrs(self):
        return self.ax_attrs

    def ask_openid(self, openid_url, return_url):
        trust_root = self.get_trust_root()
        consumer = Consumer(self.request.session, self.store_class())

        try:
            auth_request = consumer.begin(openid_url)
        except DiscoveryFailure:
            message = _('The OpenID %(url)s was invalid')
            return self.failure(message % {'url': openid_url})

        use_ax, use_sreg = discover_extensions(openid_url)
        sreg_request = None
        ax_request = None
        if use_sreg:
            sreg_attrs = self.get_sreg_attrs()
            if 'optional' not in sreg_attrs:
                sreg_attrs.update({'optional': ['nickname', 'email']})
            sreg_request = sreg.SRegRequest(**sreg_attrs)
        if use_ax:
            ax_request = ax.FetchRequest()
            ax_request.add(
                ax.AttrInfo('http://schema.openid.net/contact/email',
                            alias='email', required=True),
            )
            ax_request.add(
                ax.AttrInfo('http://schema.openid.net/namePerson/friendly',
                            alias='nickname', required=True),
            )
            ax_attrs = self.get_ax_attrs()
            for attr in ax_attrs:
                if len(attr) == 2:
                    ax_request.add(ax.AttrInfo(attr[0], required=attr[1]))
                else:
                    ax_request.add(ax.AttrInfo(attr[0]))

        if sreg_request is not None:
            auth_request.addExtension(sreg_request)
        if ax_request is not None:
            auth_request.addExtension(ax_request)
        redirect_url = auth_request.redirectURL(trust_root, return_url)
        return redirect(redirect_url)

    def failure(self, message):
        raise NotImplementedError("You need to provide an implementation "
                                  "of failure()")


class BadOpenIDStatus(Exception):
    pass


class Callback(generic.View, ReturnUrlMixin):
    def success(self):
        """
        Gets called when the OpenID authentication is successful.
        """
        raise NotImplementedError("You need to provide an implementation "
                                  "of success()")

    def failure(self, message):
        """
        Gets called when the OpenID authentication fails.
        """
        raise NotImplementedError("You need to provide an implementation "
                                  "of failure()")

    def get(self, request, *args, **kwargs):
        consumer = Consumer(request.session, DjangoOpenIDStore())
        query = dict((k, smart_unicode(v)) for k, v in request.GET.items())
        openid_response = consumer.complete(query, self.get_return_url())
        self.openid_response = openid_response

        if openid_response.status == SUCCESS:
            if 'openids' not in request.session.keys():
                request.session['openids'] = []
            request.session['openids'] = filter(
                lambda o: o.openid != openid_response.identity_url,
                request.session['openids'],
            )
            request.session['openids'].append(
                from_openid_response(openid_response),
            )
            OpenIDMiddleware().process_request(request)
            return self.success()
        elif openid_response.status == CANCEL:
            return self.failure(_('The request was cancelled'))
        elif openid_response.status == FAILURE:
            return self.failure(openid_response.message)
        elif openid_response.status == SETUP_NEEDED:
            return self.failure(_('Setup needed'))
        else:
            raise BadOpenIDStatus(openid_response.status)
