__author__ = 'fanjunwei003'
from django.conf.urls import patterns, include, url
from views import *
from django.contrib import admin

urlpatterns = patterns('fy',
    # Examples:
    # url(r'^$', 'FjwDJ.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^moneySupply/$', moneySupply,name='moneySupply'),
)
