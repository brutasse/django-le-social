from django.conf.urls.defaults import patterns, url

from . import openid_views as views


urlpatterns = patterns('',
    url(r'^openid/$', views.begin, name='openid_begin'),
    url(r'^openid/complete/$', views.callback, name='openid_callback'),
)
