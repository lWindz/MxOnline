# -*- coding: utf-8 -*-
# @author: hanzhi
# @email:  hanzhi@goldwind.com.cn
# @create: 2018/6/14 下午3:06
from captcha.fields import CaptchaField
from django import forms

from users.models import UserProfile


class LoginForm(forms.Form):
    # username非空
    username = forms.CharField(required=True)
    # 验证password长度不能小于5
    password = forms.CharField(required=True, min_length=5)


# 使用邮箱进行注册
class RegisterForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=5)
    captcha = CaptchaField(error_messages={'invalid': u'验证码错误'})


# 使用邮箱进行注册
class ForgetForm(forms.Form):
    email = forms.EmailField(required=True)
    captcha = CaptchaField(error_messages={'invalid': u'验证码错误'})


# 重置密码表单
class ModifyPwdForm(forms.Form):
    password1 = forms.CharField(required=True, min_length=5)
    password2 = forms.CharField(required=True, min_length=5)


# 修改个人用户头像表单
# 使用ModelForm，根据model自定义form
class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image']


# 修改个人用户基本信息
# 使用ModelForm，根据model自定义form
class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['nick_name', 'gender', 'birday', 'address', 'mobile']
