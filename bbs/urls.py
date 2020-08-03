"""bbs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from app01 import views
from django.views.static import serve
from bbs import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('get_code/', views.get_code),
    path('e_validate/', views.e_validate),
    path('index/', views.index),
    path('', views.start),
    path('register/', views.register),
    path('delete/', views.delete),
    path('logout/', views.logout),
    path('commit/', views.commit),
    path('backend/', views.home_backend),
    path('add_article/', views.add_article),
    path('upload/', views.upload),
    path('search/', views.search),
    path('test/', views.test),
    path('edit/', views.edit),

    re_path(r'^diggit/', views.diggit),
    re_path(r'^media/(?P<path>.*)', serve, kwargs={'document_root': settings.MEDIA_ROOT}),
    # re_path(r'^(?P<username>\w+)/tag/(?P<id>\d+)$', views.site_page),
    # re_path(r'^(?P<username>\w+)/category/(?P<id>\d+)$', views.site_page),
    # re_path(r'^(?P<username>\w+)/archive/(?P<id>\d+)$', views.site_page),
    re_path(r'^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)$', views.site_page),
    re_path(r'^(?P<username>\w+)/article/(?P<pk>\d+)$', views.article_detail),
    re_path(r'^(?P<username>\w+)$', views.site_page),
    re_path(r'^.*/', views.page_not_found),

]

