# coding=utf-8
from weixin.views import *
from django.conf.urls import patterns, include, url
from views_api import *
from django.contrib import admin

__author__ = u'范俊伟'

admin.autodiscover()

urlpatterns = patterns('weixin',
                       # Examples:
                       # url(r'^$', 'FjwDJ.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),

                       url(r'^handle/$', handleRequest, name='handleRequest'),
                       url(r'^bind/$', BindView.as_view(), name='bind'),
)
