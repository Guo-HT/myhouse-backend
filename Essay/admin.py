from django.contrib import admin
from Essay.models import *


# Register your models here.
class EssayAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ["id", "title", "content_preview", "user_name", "create_time", "watch_num", "is_checked"]
    list_filter = ["is_checked"]
    search_fields = ["id", "title", "content_preview", "user_name"]
    list_display_links = ["id", "title", "content_preview", "user_name"]

    def set_essay_unwatched(self, request, queryset):
        rows_updated = queryset.update(is_checked=False)
        self.message_user(request, f"{rows_updated}篇文章被拒绝通过审核")

    set_essay_unwatched.short_description = "设置为“不通过审核”"

    def set_watch_zero(self, request, queryset):
        row_update = queryset.update(watch_num=0)
        self.message_user(request, f"{row_update}的浏览量置0")

    set_watch_zero.short_description = "浏览量 置0"

    actions = [set_essay_unwatched, set_watch_zero]


class EssayCommentAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ["id", "comment", "from_essay", "user", "good_num", "create_time"]
    search_fields = ["comment", "from_essay", "user"]
    list_display_links = ["id", "comment", "from_essay", "user"]

    def set_good_zero(self, request, queryset):
        row_update = queryset.update(good_num=0)
        self.message_user(request, f"{row_update}的点赞量置0")

    set_good_zero.short_description = "点赞量 置0"

    def delete(self, request, queryset):
        rows_delete = queryset.delete()
        self.message_user(request, f"{rows_delete[0]}条数据被删除。")

    delete.short_description = "删除选中的 评论"

    actions = [set_good_zero, delete]


class EssayCommentReplyAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ["id", "reply", "from_comment", "reply_to", "user", "good_num", "create_time"]
    search_fields = ["reply", "from_comment", "reply_to", "user"]
    list_display_links = ["id", "reply", "from_comment", "reply_to", "user"]

    def set_good_zero(self, request, queryset):
        row_update = queryset.update(good_num=0)
        self.message_user(request, f"{row_update}的点赞量置0")

    set_good_zero.short_description = "点赞量 置0"

    def delete(self, request, queryset):
        rows_delete = queryset.delete()
        self.message_user(request, f"{rows_delete[0]}条数据被删除。")

    delete.short_description = "删除选中的 评论回复"

    actions = [set_good_zero, delete]


class GoodListAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ["id", "essay", "user", "time"]
    search_fields = ["essay", "user"]
    list_display_links = ["id", "essay", "user"]

    def delete(self, request, queryset):
        rows_delete = queryset.delete()
        self.message_user(request, f"{rows_delete[0]}条数据被删除。")

    delete.short_description = "删除选中的 点赞记录"

    actions = [delete]


class BrowseHistoryAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ["id", "essay", "user", "time", "ip"]
    search_fields = ["essay", "user", "ip"]
    list_display_links = ["id", "essay", "user"]


class EssayCollectionAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ["id", "essay", "user", "time"]
    search_fields = ["essay", "user"]
    list_display_links = ["id", "essay", "user"]

    def delete(self, request, queryset):
        rows_delete = queryset.delete()
        self.message_user(request, f"{rows_delete[0]}条数据被删除。")

    delete.short_description = "删除选中的 收藏记录"

    actions = [delete]


admin.site.register(Essay, EssayAdmin)
admin.site.register(EssayComment, EssayCommentAdmin)
admin.site.register(EssayCommentReply, EssayCommentReplyAdmin)
admin.site.register(GoodList, GoodListAdmin)
admin.site.register(BrowseHistory, BrowseHistoryAdmin)
admin.site.register(EssayCollection, EssayCollectionAdmin)
