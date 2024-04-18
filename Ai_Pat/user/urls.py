from django.urls import path
from .views import login, join, get_user_info, update_userinfo_password, user_delete, update_userinfo_username, confirm_email, confirm_new_email, update_userinfo_email

urlpatterns = [
    path('login', login),
    path('join', join),
    path('get_user_info', get_user_info),
    path('update_userinfo_password', update_userinfo_password),
    path('update_userinfo_username', update_userinfo_username),
    path('update_userinfo_email', update_userinfo_email),
    path('confirm_new_email/<str:token>/', confirm_new_email, name='confirm_new_email'),
    path('user_delete', user_delete),
    path('confirm_email/<str:token>/', confirm_email, name='confirm_email'),
]