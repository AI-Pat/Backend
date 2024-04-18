import os
import datetime
from django.conf import settings
import jwt
from rest_framework import status

from .exception import TokenExtractException, TokenValidException
from .models import User


def has_token(token):
    return "Bearer" not in token


def token_encode(user):
    # 깃헙 키스토어 활용시
    SECRET_KEY = getattr(settings, 'JWT_SECRET')
    JWT_EXPIRED_DAY = getattr(settings, 'JWT_EXPIRED_DAY')
    JWT_ALGORITHM = getattr(settings, 'JWT_ALGORITHM')

    jwt_token = jwt.encode(payload={'id': user.id,
                                    'username': user.username,
                                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=int(JWT_EXPIRED_DAY))},
                           key=SECRET_KEY,
                           algorithm=JWT_ALGORITHM)

    return jwt_token


def token_decode(token):
    SECRET_KEY = getattr(settings, 'JWT_SECRET')
    JWT_ALGORITHM = getattr(settings, 'JWT_ALGORITHM')

    if has_token(token):
        raise TokenExtractException(status=status.HTTP_401_UNAUTHORIZED, message='토큰이 존재하지 않습니다.')

    token_split = token.split(' ')
    jwt_token = token_split[1]
    decode = jwt.decode(jwt_token, key=SECRET_KEY, algorithms=[JWT_ALGORITHM])
    user = User.objects.get(username=decode['username'])

    if not user:
        raise TokenValidException(status=status.HTTP_401_UNAUTHORIZED, message='토큰이 유효하지 않습니다.')

    return user
    # try:
    #     token_split = token.split(' ')
    #     jwt_token = token_split[1]
    #     decode = jwt.decode(jwt_token, key=SECRET_KEY, algorithms=[JWT_ALGORITHM])
    #     user = User.objects.get(username=decode['username'])
    #
    #     if not user:
    #         raise TokenValidException(status=status.HTTP_401_UNAUTHORIZED, message='토큰이 유효하지 않습니다.')
    #
    #     return user
    #
    # except:
    #     raise TokenValidException(status=status.HTTP_401_UNAUTHORIZED, message='토큰이 유효하지 않습니다.')