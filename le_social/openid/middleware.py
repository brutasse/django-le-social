class OpenIDMiddleware(object):
    """
    Populates request.openid and request.openids
    """

    def process_request(self, request):
        request.openids = request.session.get('openids', [])
