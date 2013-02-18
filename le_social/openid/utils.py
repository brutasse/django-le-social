import time

try:
    from openid.consumer.discover import discover
    from openid.extensions import sreg, ax
    from openid.yadis import xri
except ImportError:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured(
        "python-openid is required to use le_social.openid"
    )

from django.http import get_host
from django.utils.html import escape


class OpenID(object):
    def __init__(self, openid, issued, attrs=None, sreg_=None, ax_=None):
        self.openid = openid
        self.issued = issued
        self.attrs = attrs or {}
        self.sreg = sreg_ or {}
        self.ax = ax_ or {}
        self.is_iname = (xri.identifierScheme(openid) == 'XRI')

    def __repr__(self):
        return '<OpenID: %s>' % self.openid

    def __str__(self):
        return self.openid


def get_url_host(request):
    scheme = 'https' if request.is_secure() else 'http'
    host = escape(get_host(request))
    return '%s://%s' % (scheme, host)


def discover_extensions(openid_url):
    service = discover(openid_url)
    use_ax = False
    use_sreg = False
    for endpoint in service[1]:
        if not use_sreg:
            use_sreg = sreg.supportsSReg(endpoint)
        if not use_ax:
            use_ax = endpoint.usesExtension("http://openid.net/srv/ax/1.0")
        if use_ax and use_sreg:
            break
    if not use_sreg and not use_ax:
        use_sreg = True
    return use_ax, use_sreg


def from_openid_response(openid_response):
    issued = int(time.time())
    sreg_resp = (sreg.SRegResponse.fromSuccessResponse(openid_response) or
                 [])
    ax_resp = ax.FetchResponse.fromSuccessResponse(openid_response)
    ax_args = {}
    if ax_resp is not None:
        ax_args = ax_resp.getExtensionArgs()
        ax_resp.parseExtensionArgs(ax_args)
        ax_args = ax_resp.data

    return OpenID(
        openid_response.identity_url, issued, openid_response.signed_fields,
        dict(sreg_resp), ax_args,
    )
