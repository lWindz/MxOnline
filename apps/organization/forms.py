# -*- coding: utf-8 -*-
# @author: hanzhi
# @email:  hanzhi@goldwind.com.cn
# @create: 2018/7/31 下午5:11
import re

from django import forms

from operation.models import UserAsk


class UserAskForm(forms.ModelForm):
    class Meta:
        model = UserAsk
        fields = ['name', 'mobile', 'course_name']

    def clean_mobile(self):
        """
        正则表达式验证手机号码是否合法
        :return:
        """
        mobile = self.cleaned_data['mobile']
        REGEX_MOBILE = "^1[358]\d{9}$|^147\d{8}$|^176\d{8}$"
        p = re.compile(REGEX_MOBILE)
        if p.match(mobile):
            return mobile
        else:
            # code自定义的
            return forms.ValidationError(u'手机号码非法', code='mobile_invalid')
