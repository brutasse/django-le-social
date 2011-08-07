from django.conf.urls.defaults import patterns, url

from . import registration_views as views

urlpatterns = patterns('',
    url(r'^activate/complete/$', views.activation_complete,
        name='registration_activation_complete'),

    url(r'^activate/(?P<activation_key>\w+)/$', views.activate,
        name='registration_activate'),

    url(r'^activate-expired/(?P<activation_key>\w+)/$', views.activate_expired,
        name='registration_activate_expired'),

    url(r'^register/$', views.register,
        name='registration_register'),

    url(r'^register-notify/$', views.register_with_notification,
        name='registration_register_with_notification'),

    url(r'^register-closed/$', views.register_but_closed,
        name='registration_register_but_closed'),

    url(r'^register/complete/$', views.registration_complete,
        name='registration_complete'),

    url(r'^register/closed/$', views.registration_closed,
        name='registration_closed'),
)
