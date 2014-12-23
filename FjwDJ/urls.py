from django.conf.urls import patterns, include, url

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'FjwDJ.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^fy/', include('fy.urls',namespace='fy')),
    url(r'^weixin/', include('weixin.urls',namespace='weixin')),
    url(r'^$', 'fy.views.home', name='home'),
    url(r'^fyadmin/', include('FYAdmin.urls',namespace='fyadmin')),
    url(r'^android/', include('android.urls',namespace='android')),
)
