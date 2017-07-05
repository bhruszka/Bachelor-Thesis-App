from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.gallery, name='gallery'),
    url(r'^(.+?)/details/$', views.details, name='details'),
    url(r'^(.+?)/details/#(?[0-9)$', views.details, name='details')
]