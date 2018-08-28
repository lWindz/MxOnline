# -*- coding: utf-8 -*-
# @author: hanzhi
# @email:  hanzhi@goldwind.com.cn
# @create: 2018/8/14 下午3:31


from django.conf.urls import url

from users.views import UserInfoView, UploadImageView, UploadPwdView, SendEmailCodeView, UpdateEmailView, MyCourseView, \
    MyFavOrgView, MyFavTeacherView, MyFavCourseView, MymessageView

urlpatterns = [
    # 课程机构列表页
    url(r'^info/$', UserInfoView.as_view(), name='user_info'),

    # 用户头像上传
    url(r'^iamge/upload/$', UploadImageView.as_view(), name='image_upload'),

    # 用户个人中心修改密码
    url(r'^update/pwd/$', UploadPwdView.as_view(), name='update_pwd'),

    # 发送邮箱验证码
    url(r'^sendemail_code/$', SendEmailCodeView.as_view(), name='sendemail_code'),

    # 修改密码
    url(r'^update_email/$', UpdateEmailView.as_view(), name='update_email'),

    # 我的课程
    url(r'^mycourse/$', MyCourseView.as_view(), name='mycourse'),

    # 我收藏的课程机构
    url(r'^myfav/org/$', MyFavOrgView.as_view(), name='myfav_org'),

    # 我收藏的授课讲师
    url(r'myfav/teacher/$', MyFavTeacherView.as_view(), name='myfav_teacher'),

    # 我收藏的课程
    url(r'^myfav/course/$', MyFavCourseView.as_view(), name='myfav_course'),

    # 我的消息
    url(r'^mymessage/$', MymessageView.as_view(), name='mymessage'),
]
