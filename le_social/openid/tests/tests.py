try:
    from unittest import skipIf
except ImportError:
    from django.utils.unittest import skipIf

try:
    from openid.consumer import consumer
    from openid.message import Message
    from .. import utils
    openid = True
except ImportError:
    openid = False

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django.test import TestCase


def discover_extensions(openid_url):
    """
    Don't bother with extensions for tests.
    """
    return False, False


class OpenidRequest(object):
    """
    Fake OpenID request
    """
    def __init__(self, url):
        self.url = url

    def addExtension(self, sreg_request):
        pass

    def redirectURL(self, trust_root, return_url):
        return trust_root[:-1] + return_url


class OpenidResponse(object):
    """
    Fake OpenID response
    """
    def __init__(self, status, message):
        self.status = status
        self.message = message
        self.identity_url = 'http://bruno.renie.fr'
        self.signed_fields = None

    def getSignedNS(self, uri):
        return self.message.getArgs(uri)

    def extensionResponse(self, namespace_uri, require_signed):
        if require_signed:
            return self.getSignedNS(namespace_uri)
        else:
            return self.message.getArgs(namespace_uri)


class Consumer(object):
    """
    Fake OpenID consumer
    """
    def __init__(self, session, store_class):
        self.session = session
        self.store_class = store_class

    def begin(self, url):
        return OpenidRequest(url)

    def complete(self, query, return_url):
        if not query:
            return OpenidResponse(consumer.FAILURE, 'Invalid openid.mode')
        return OpenidResponse(consumer.SUCCESS, Message())


class OpenidTest(TestCase):
    urls = 'le_social.openid.tests.urls'

    def setUp(self):
        self._real_consumer = consumer.Consumer
        consumer.Consumer = Consumer

        self._real_discover_extensions = utils.discover_extensions
        utils.discover_extensions = discover_extensions

    def tearDown(self):
        consumer.Consumer = self._real_consumer
        utils.discover_extensions = self._real_discover_extensions

    def test_openid_assoc(self):
        url = reverse('openid_begin')
        response = self.client.get(url)
        self.assertContains(response, '<form ')
        data = {'openid_url': 'http://bruno.renie.fr'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

    def test_failed_callback(self):
        url = reverse('openid_callback')
        response = self.client.get(url)
        self.assertContains(response, 'Invalid openid.mode')

    def test_successful_callback(self):
        url = reverse('openid_callback') + '?type=success'
        response = self.client.get(url)
        self.assertContains(response, 'OpenID association')
OpenidTest = skipIf(not openid, "openid not installed")(OpenidTest)
