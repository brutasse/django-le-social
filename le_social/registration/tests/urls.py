from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^activate/complete/$', views.activation_complete,
        name='registration_activation_complete'),

    url(r'^activate/(?P<activation_key>.+)/$', views.activate,
        name='registration_activate'),

    url(r'^activate-expired/(?P<activation_key>.+)/$', views.activate_expired,
        name='registration_activate_expired'),

    url(r'^register/$', views.register,
        name='registration_register'),

    url(r'^register-no-notify/$', views.register_with_no_notification,
        name='registration_register_with_notification'),

    url(r'^register-closed/$', views.register_but_closed,
        name='registration_register_but_closed'),

    url(r'^register-expired/$', views.register_expired,
        name='registration_register_expired'),

    url(r'^register/complete/$', views.registration_complete,
        name='registration_complete'),

    url(r'^register/closed/$', views.registration_closed,
        name='registration_closed'),
]
