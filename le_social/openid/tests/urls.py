from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns(
    '',
    url(r'^openid/$', views.begin, name='openid_begin'),
    url(r'^openid/complete/$', views.callback, name='openid_callback'),
)
