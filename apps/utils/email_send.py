# -*- coding: utf-8 -*-
# @author: hanzhi
# @email:  hanzhi@goldwind.com.cn
# @create: 2018/6/15 下午4:46
from random import Random

from django.core.mail import send_mail

from MxOnline.settings import EMAIL_FROM
from users.models import EmailVerifyRecord


# 产生邮件验证码,从字母和数字中随机选择一位，拼起来作为邮件验证码
def random_str(randomlength=8):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    print random
    print randomlength
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


def send_register_email(email, send_type='register'):
    # 实例化一个email验证对象
    email_record = EmailVerifyRecord()
    if send_type == 'update_email':
        code = random_str(4)
    else:
        code = random_str(16)
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    email_record.save()
    email_title = ''
    email_body = ''
    if send_type == 'register':
        email_title = u'MX在线网注册激活链接'
        email_body = u'请点击下面链接激活你的账号：http://127.0.0.1:9000/active/{0}'.format(code)
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass
    elif send_type == 'forget':
        email_title = u'MX在线网注册密码重置链接'
        email_body = u'请点击下面的链接重置密码：http://127.0.0.1:9000/reset/{0}'.format(code)
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass
    elif send_type == 'update_email':
        email_title = u'MX在线邮箱修改验证码'
        email_body = u'你的邮箱验证码为：{0}'.format(code)
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass
