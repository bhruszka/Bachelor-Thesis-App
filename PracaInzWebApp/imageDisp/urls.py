from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.gallery, name='gallery'),
    url(r'^(?P<imageName>.+?)/details/$', views.details, name='details'),
    url(r'^(?P<imageName>.+?)/details/(?P<tab>[1-3]{1})$', views.details, name='details'),
]