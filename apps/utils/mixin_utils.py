# -*- coding: utf-8 -*-
# @author: hanzhi
# @email:  hanzhi@goldwind.com.cn
# @create: 2018/8/8 上午11:27
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class LoginRequiredMixin(object):

    @method_decorator(login_required(login_url='/login/'))
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)
