from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    url(r'^$', views.gallery, name='gallery'),
    url(r'^add/$', views.add, name='add'),
    url(r'^(?P<imageName>.+?)/details/$', views.details, name='details'),
    url(r'^(?P<imageName>.+?)/details/(?P<tab>[1,2]{1})$', views.details, name='details'),
    url(r'^(?P<imageName>.+?)/details/3$', views.teeth_view, name='teeth_view'),
    url(r'^(?P<imageName>.+?)/details/4$', views.edit, name='edit'),
]