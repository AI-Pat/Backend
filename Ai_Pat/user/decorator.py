import os
from functools import wraps

from .exception import TokenExtractException, TokenValidException
from .token import token_decode
from rest_framework.response import Response


def authenticated(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        HTTP_AUTHORIZATION = 'HTTP_AUTHORIZATION'

        try:
            token = request.META.get(HTTP_AUTHORIZATION)
            request.user = token_decode(token)
        except TokenExtractException as e:
            return Response({'status': e.status, 'message': e.message}, status=e.status)

        except TokenValidException as e:
            return Response({'status': e.status, 'message': e.message}, status=e.status)

        return function(request, *args, **kwargs)

    return wrap