# coding=utf-8
# Date: 14/11/21
# Time: 09:11
# Email:fanjunwei003@163.com
from django.conf.urls import patterns, url
from views import *

__author__ = u'范俊伟'

urlpatterns = patterns('android',
                       url(r'^login$', LoginView.as_view(), name='login'),
                       url(r'^users', UsersView.as_view(), name='users'),

)
