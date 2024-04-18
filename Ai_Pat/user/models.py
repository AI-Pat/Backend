from django.utils import timezone
from django.db import models

class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True, null=False)
    password = models.CharField(max_length=256, null=False)
    email = models.CharField(max_length=256, unique=True, null=False)
    new_email = models.CharField(max_length=256, null=True, blank=True)  # 새 이메일 주소 임시 저장 필드
    name = models.CharField(max_length=50)
    email_token = models.CharField(max_length=256, null=True, blank=True)  # 이메일 인증 토큰 필드

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    is_active = models.BooleanField(default=False)

    def str(self):
        return f'{self.username}계정'