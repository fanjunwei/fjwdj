# coding=utf-8
# Date: 14/11/21
# Time: 09:11
# Email:fanjunwei003@163.com
from django.conf.urls import patterns, url
from views import *

__author__ = u'范俊伟'

urlpatterns = patterns('fyadmin',
                       url(r'^img_code/$', get_img_code, name='img_code'),
                       url(r'^register/$', RegisterView.as_view(), name='register'),
                       url(r'^logout/$', logout, name='logout'),
                       url(r'^$', HomeView.as_view(), name='home'),
                       url(r'^change_password/$', ChangePasswordView.as_view(), name='change_password'),
)
