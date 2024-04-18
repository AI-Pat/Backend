# Create your views here.

import json
import re
import uuid

import bcrypt
from django.core.mail import send_mail
from dotenv import load_dotenv
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .decorator import authenticated
from .models import User
from .token import token_encode
from drf_yasg import openapi

load_dotenv()


# Create your views here.
class LoginRequest:
    def __init__(self, body):
        self.username = body['username']
        self.password = body['password']


class JoinRequest:
    def __init__(self, body):
        self.username = body['username']
        self.password = body['password']
        self.email = body['email']
        self.name = body['name']

login_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING, description='사용자 이름'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, description='비밀번호'),
    }
)

@swagger_auto_schema(method='post', request_body=login_request_body, responses={200: '로그인에 성공했습니다.', 401: '로그인에 실패했습니다.'})
@api_view(['POST'])
def login(request):
    dto = LoginRequest(json.loads(request.body))
    try:
        user = User.objects.get(username=dto.username)
    except User.DoesNotExist:
        return Response({"message": "로그인에 실패했습니다."}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.is_active:
        return Response({"message": "이메일을 인증해주세요."}, status=status.HTTP_401_UNAUTHORIZED)

    hashed_password = bytes(user.password, 'utf-8')
    if not bcrypt.checkpw(bytes(dto.password, 'utf-8'), hashed_password):
        return Response({"message": "아이디 또는 비밀번호가 틀렸습니다."}, status=status.HTTP_401_UNAUTHORIZED)

    token = token_encode(user)

    return Response({"message": "로그인에 성공했습니다.", "token": token})


@api_view(['POST'])
@swagger_auto_schema(responses={200: 'OK'})
def join(request):
    dto = JoinRequest(json.loads(request.body))
    print(dto)
    # validation 필요!

    # 이미 가입된 아이디인지 검증
    username_validation = User.objects.filter(username=dto.username)
    print(User.objects)
    if username_validation:
        return Response({"message": "아이디가 이미 존재합니다."}, status=status.HTTP_400_BAD_REQUEST)

    # 이미 가입된 이메일인지 검증
    email_validation = User.objects.filter(email=dto.email)
    if email_validation:
        return Response({"message": "이메일이 이미 존재합니다."}, status=status.HTTP_400_BAD_REQUEST)
    pwd = dto.password
    if len(pwd) < 10:
        return Response({"message": "비밀번호는 최소 10자 이상이어야 함"}, status=status.HTTP_400_BAD_REQUEST)
    elif re.search('[0-9]+', pwd) is None:
        return Response({"message": "비밀번호는 최소 1개 이상의 숫자가 포함되어야 함"}, status=status.HTTP_400_BAD_REQUEST)
    elif re.search('[a-zA-Z]+', pwd) is None:
        return Response({"message": "비밀번호는 최소 1개 이상의 영문 대소문자가 포함되어야 함"}, status=status.HTTP_400_BAD_REQUEST)
    elif re.search('[`~!@#$%^&*(),<.>/?]+', pwd) is None:
        return Response({"message": "비밀번호는 최소 1개 이상의 특수문자가 포함되어야 함"}, status=status.HTTP_400_BAD_REQUEST)
    pw_hash = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())

    email_token = uuid.uuid4()
    email_message = f'''
    아래 링크를 클릭하여 이메일을 인증해주세요.
    210.124.196.57:8000/api/auth/emailAuth/{email_token}
    '''
    send_mail(
        '이메일 인증 메시지',
        email_message,
        'no-reply@mywebsite.com',
        [dto.email],
        fail_silently=False,
    )
    user = User(username=dto.username, password=pw_hash.decode('utf-8'), email=dto.email, name=dto.name,
                email_token=email_token)
    user.save()

    return Response({"message": "이메일을 인증을 해주세요!"}, status=status.HTTP_201_CREATED)

@api_view(['PUT'])
@authenticated
def update_userinfo_email(request):
    body = json.loads(request.body)
    user = User.objects.get(username=request.user.username)
    new_email = body['email']
    if request.user.email == new_email:
        return Response({"message": "새 이메일이 현재 이메일과 동일합니다. 다른 이메일을 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        email_validation = User.objects.filter(email=new_email)
        if email_validation:
            return Response({"message": "이메일이 이미 존재합니다."}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            email_token = uuid.uuid4()
            email_message = f'''
            아래 링크를 클릭하여 이메일을 인증해주세요.
            https://www.cgvgoat.xyz/auth/emailAuth/{email_token}
            '''
            send_mail(
                '이메일 인증 메시지',
                email_message,
                'no-reply@mywebsite.com',
                [new_email],
                fail_silently=False,
            )
            user.new_email = new_email  # 새 이메일 주소 임시 저장
            user.email_token = str(email_token)  # 이메일 인증 토큰 저장
            user.is_active = False
            user.save()

    return Response({"message": "이메일 인증을 완료해주세요!"}, status=status.HTTP_200_OK)

@api_view(['GET'])
def confirm_email(request, token):
    print("Confirm email view called")
    try:
        user = User.objects.get(email_token=token)
        user.is_active = True
        user.save()
        return Response({"message": "이메일이 성공적으로 인증되었습니다."}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"message": "잘못된 접근입니다."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def confirm_new_email(request, token):
    print("Confirm email view called")
    try:
        user = User.objects.get(email_token=token)  # 인증 토큰으로 사용자 조회
        user.email = user.new_email  # 이메일 변경
        user.is_active = True
        user.new_email = None  # 이메일 변경 후 new_email 필드 초기화
        user.email_token = None  # 이메일 변경 후 email_token 필드 초기화
        user.save()
        return Response({"message": "이메일이 성공적으로 변경되었습니다."}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"message": "잘못된 접근입니다."}, status=status.HTTP_400_BAD_REQUEST)
@api_view(['DELETE'])
@authenticated
def user_delete(request):
    User.objects.get(username=request.user.username).delete()
    return Response({"회원탈퇴 완료"}, status=status.HTTP_204_NO_CONTENT)

user_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING, description='User name'),
        'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email'),
        'username': openapi.Schema(type=openapi.TYPE_STRING, description='User username'),
    }
)

@swagger_auto_schema(methods=['post'], responses={200: user_response})
@api_view(["POST"])
@authenticated
def get_user_info(request):
    return Response({
        "name": request.user.name,
        "email": request.user.email,
        "username": request.user.username
    })


@api_view(['PUT'])
@authenticated
def update_userinfo_password(request):
    body = json.loads(request.body)

    # 현재 비밀번호 검증
    current_password = body['current_password']
    if not bcrypt.checkpw(current_password.encode('utf-8'), request.user.password.encode('utf-8')):
        return Response({"message": "현재 비밀번호가 일치하지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED)

    # 새로운 비밀번호 검증
    new_password = body['new_password']
    if len(new_password) < 10:
        return Response({"message": "비밀번호는 최소 10자 이상이어야 함"}, status=status.HTTP_401_UNAUTHORIZED)
    elif re.search('[0-9]+', new_password) is None:
        return Response({"message": "비밀번호는 최소 1개 이상의 숫자가 포함되어야 함"}, status=status.HTTP_401_UNAUTHORIZED)
    elif re.search('[a-zA-Z]+', new_password) is None:
        return Response({"message": "비밀번호는 최소 1개 이상의 영문 대소문자가 포함되어야 함"}, status=status.HTTP_401_UNAUTHORIZED)
    elif re.search('[`~!@#$%^&*(),<.>/?]+', new_password) is None:
        return Response({"message": "비밀번호는 최소 1개 이상의 특수문자가 포함되어야 함"}, status=status.HTTP_401_UNAUTHORIZED)

    # 비밀번호 변경
    pw_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    request.user.password = pw_hash.decode('utf-8')
    request.user.save()

    return Response({"message": "회원 수정을 성공했습니다."})



@api_view(['PUT'])
@authenticated
def update_userinfo_username(request):
    body = json.loads(request.body)
    user = User.objects.get(username=request.user.username)  # user db
    new_name = body['name']  # put name
    if request.user.name == new_name:
        pass
    else:
        name_validation = User.objects.filter(name=new_name)
        if name_validation:
            return Response({"message": "이름이 이미 존재합니다."}, status=status.HTTP_401_UNAUTHORIZED)
    user.name = new_name
    user.save()

    return Response({"message": "회원 수정을 성공했습니다."})

