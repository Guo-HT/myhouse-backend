from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt
from UserManagement import views

# /user/*
urlpatterns = [
    re_path("^reg", views.Reg.as_view()),
    re_path("^log", views.Log.as_view()),
    re_path("^change", views.ChgPwd.as_view()),
    re_path("^addPhoto", views.add_photo, name="add_photo"),
    re_path("^user_status", views.user_status, name="user_status"),
    re_path("^get_info", views.get_info, name="get_info"),
    re_path("^service_log", csrf_exempt(views.ServiceLog.as_view()), name="service_log"),  # 客服

]
