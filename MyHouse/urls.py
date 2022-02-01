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
from django.conf.urls.static import static
from MyHouse import settings
from MyHouse import views

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path("user/", include("UserManagement.urls")),
    re_path("data/", include("Data.urls")),
    re_path("essay/", include("Essay.urls")),
    re_path("^csrf_token", views.csrf_token, name="csrf_token"),  # 状态测试接口
    re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
