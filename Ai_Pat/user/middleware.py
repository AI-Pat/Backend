class BearerTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if token and not token.startswith("Bearer "):
            # Bearer 추가
            request.META['HTTP_AUTHORIZATION'] = f"Bearer {token}"
        response = self.get_response(request)
        return response