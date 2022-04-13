from django.urls import path, re_path
from Essay import views
from django.conf.urls import include


# /essay/*
urlpatterns = [
    re_path("^test", views.test, name="test"),
    re_path("^details$", views.get_list, name="get_list"),  # 列表
    re_path("^detail", views.EssayDetail.as_view(), name="detail"),  # 某篇
    re_path("^do_good", views.do_good, name="do_good"),  # 文章点赞
    re_path("^do_collect", views.do_collect, name="do_collect"),  # 文章收藏
    re_path("^comment", views.Comment.as_view(), name="comment"),
    re_path("^reply", views.Reply.as_view(), name="reply"),
    re_path("^c_r_good$", views.comment_reply_good),  # 评论及回复点赞
    re_path("^get_per_info_list$", views.get_per_info_list),  # 评论及回复点赞
    re_path("^richtext_upload", views.richtext_upload, name="richtext_upload"),
    # re_path("^essays", views.autocomplete, name="essays"),  # 官方文档样例
    # re_path("^essays", views.ContentSearch(), name="essays"),  # 重写类
    # re_path("^essays", include("haystack.urls")),  # mvc，自动调用/templates/search/search.html
]
