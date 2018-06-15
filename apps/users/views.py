# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.shortcuts import render

from django.views.generic.base import View

from users.forms import LoginForm, RegisterForm
from users.models import UserProfile
from utils.email_send import send_register_email


# 重写django的authenticate认证方法，改成用邮箱登录
class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 用户名为输入账号，或邮箱为输入账号，并且密码为密码，这里django的password加密，不能直接=比较，Q(password=password)仅举例，该处不能使用
            # user = UserProfile.objects.get(Q(username=username) | Q(email=username), Q(password=password))
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


# 基于类view的登录
class LoginView(View):
    def get(self, request):
        return render(request, 'login.html', {})

    def post(self, request):
        # 自定义form
        login_form = LoginForm(request.POST)
        # 验证form表单
        if login_form.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return render(request, 'index.html')
            else:
                return render(request, 'login.html', {'msg': '用户名或密码错误'})
        else:
            return render(request, 'login.html', {'login_form': login_form})


# 注册功能
class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        return render(request, 'register.html', {'register_form': register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            username = request.POST.get('email', '')
            password = request.POST.get('password', '')
            # 实例化一个UserProfile对象
            user_profile = UserProfile()
            user_profile.username = username
            user_profile.email = username
            # 注册时，对明文密码进行加密
            user_profile.password = make_password(password)
            # save保存到数据库中
            user_profile.save()
            send_register_email(username, 'register')
            return render(request, 'index.html')

# 基于方法的登录
# def user_login(request):
#     if request.method == 'POST':
#         username = request.POST.get('username', '')
#         password = request.POST.get('password', '')
#         user = authenticate(username=username, password=password)
#         if user is not None:
#             login(request, user)
#             return render(request, 'index.html')
#         else:
#             return render(request, 'login.html', {'msg': '用户名或密码错误'})
#     elif request.method == 'GET':
#         return render(request, 'login.html', {})
