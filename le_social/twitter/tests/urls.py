from django.conf.urls.defaults import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^oauth/authorize/$', views.authorize, name='authorize'),
    url(r'^oauth/callback/$', views.callback, name='callback'),
)
