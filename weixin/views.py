# coding=utf-8
# Date: 14/12/6
# Time: 14:47
# Email:fanjunwei003@163.com
from django.contrib.auth import authenticate
from django.contrib import messages
from django.views.generic import TemplateView
from weixin.models import WeiXinUser

__author__ = u'范俊伟'


class BindView(TemplateView):
    template_name = 'weixin/bind.html'

    def get(self, request, *args, **kwargs):
        openid = request.REQUEST.get('openid')
        if not openid:
            self.template_name = 'weixin/bind_error.html'
        return super(BindView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        openid = request.REQUEST.get('openid')
        if not openid:
            self.template_name = 'weixin/bind_error.html'
            return self.get(request, *args, **kwargs)

        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            weixinUser = WeiXinUser.objects.get(weixinid=openid)
        except WeiXinUser.DoesNotExist:
            weixinUser = None
        if not weixinUser:
            messages.error(request, u'请求错误,请返回重新绑定')
            return self.get(request, *args, **kwargs)

        user = authenticate(username=username,
                            password=password)
        if not user or not user.is_active:
            messages.error(request, u'用户名或密码错误')
            return self.get(request, *args, **kwargs)
        else:
            weixinUser.user_id = user.pk
            weixinUser.save()
            self.template_name = 'weixin/bind_success.html'
            return self.get(request, *args, **kwargs)


