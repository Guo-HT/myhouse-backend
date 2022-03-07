"""MyHouse URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.conf.urls import include, url
from django.views import static
from MyHouse import settings
from MyHouse import views
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    re_path("user/", include("UserManagement.urls")),
    re_path("data/", include("Data.urls")),
    re_path("essay/", include("Essay.urls")),
    re_path("^csrf_token", views.csrf_token, name="csrf_token"),  # 状态测试接口
    re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^favicon\.ico', RedirectView.as_view(url=r'/static/img/favicon.ico')),
    url(r'^robots\.txt', RedirectView.as_view(url=r'/static/robots.txt')),
    url(r'^silk/', include('silk.urls', namespace='silk')),  # 性能监测
]

if settings.DEBUG is False:
    urlpatterns += url(r'^static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT}, name='static'),
    urlpatterns += url(r'^upload_files/(?P<path>.*)$', static.serve, {'document_root':settings.MEDIA_ROOT}, name='upload_files'),
