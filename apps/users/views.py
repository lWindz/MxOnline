# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.shortcuts import render

from django.views.generic.base import View

from users.forms import LoginForm, RegisterForm, ForgetForm, ModifyPwdForm
from users.models import UserProfile, EmailVerifyRecord
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
                if user.is_active:
                    login(request, user)
                    return render(request, 'index.html')
                else:
                    return render(request, 'login.html', {'msg': '用户未激活'})
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
            if UserProfile.objects.filter(email=username):
                return render(request, 'register.html', {'register_form': register_form, 'msg': '用户已经存在'})
            password = request.POST.get('password', '')
            # 实例化一个UserProfile对象
            user_profile = UserProfile()
            user_profile.username = username
            user_profile.email = username
            # 注册时，对明文密码进行加密
            user_profile.password = make_password(password)
            # 表明用户还未激活，用户在点击链接之后才会激活
            user_profile.is_active = False
            # save保存到数据库中
            user_profile.save()
            send_register_email(username, 'register')
            return render(request, 'login.html')
        else:
            return render(request, 'register.html', {'register_form': register_form})


# 点击邮件中的链接以激活用户
class ActiveUserView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
            return render(request, 'login.html')
        else:
            return render(request, 'active_fail.html')
        return render(request, 'index.html')


# 忘记密码接口
class ForgetPwdView(View):
    def get(self, request):
        forget_form = ForgetForm()
        return render(request, 'forgetpwd.html', {'forget_form': forget_form})

    def post(self, request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get('email', '')
            send_register_email(email, 'forget')
            return render(request, 'send_success.html')
        else:
            return render(request, 'forgetpwd.html')


# 重置密码
class ResetView(View):
    def get(self, request, reset_code):
        all_records = EmailVerifyRecord.objects.filter(code=reset_code)
        if all_records:
            for record in all_records:
                # 判断邮件链接是否失效，1为失效
                if record.used == 1:
                    return render(request, 'email_timeout.html')
                email = record.email
                return render(request, 'password_reset.html', {'email': email})
        else:
            return render(request, 'active_fail.html')
        return render(request, 'index.html')


class ModifyPwdView(View):
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            email = request.POST.get('email', '')
            if pwd1 != pwd2:
                return render(request, 'password_reset.html', {'email': email, 'msg': '密码不一致'})
            else:
                user = UserProfile.objects.get(email=email)
                user.password = make_password(pwd2)
                user.save()
                email_record = EmailVerifyRecord.objects.filter(email=email).order_by('-send_time')[0]
                # 修改密码成功后，将邮箱链接变为失效
                email_record.used = 1
                email_record.save()
                return render(request, 'login.html')
        else:
            email = request.POST.get('email', '')
            return render(request, 'password_reset.html', {'email': email, 'modify_form': modify_form})

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
