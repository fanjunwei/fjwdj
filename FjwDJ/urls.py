from django.conf.urls import patterns, include, url

from django.contrib import admin
from util.task import startTask

admin.autodiscover()
startTask()
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'FjwDJ.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^fy/', include('fy.urls')),
    url(r'^weixin/', include('weixin.urls')),
    url(r'^$', 'fy.views.home', name='home'),
    url(r'^fyadmin/', include('FYAdmin.urls',namespace='fyadmin')),
)
