# -*- coding: utf-8 -*-
# @author: hanzhi
# @email:  hanzhi@goldwind.com.cn
# @create: 2018/6/14 下午3:06
from captcha.fields import CaptchaField
from django import forms


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
