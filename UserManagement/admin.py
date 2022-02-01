from django.contrib import admin
from UserManagement.views import *


# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ['id', "name", 'email', 'head_photo_show', 'reg_time', 'is_active']
    list_filter = ['is_active']
    search_fields = ['id', "name", 'email']
    list_display_links = ['id', "name", 'email']


class ServiceAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ['id', "name", 'email', 'reg_time', 'is_active']
    list_filter = ['is_active']
    search_fields = ['id', "name", 'email']
    list_display_links = ['id', "name", 'email']

    def set_service_inactive(self, request, queryset):
        rows_updated = queryset.update(is_active=False)
        self.message_user(request, f"{rows_updated}位客服被下岗")

    set_service_inactive.short_description = "设置为“非活跃客服”"

    def set_service_active(self, request, queryset):
        rows_updated = queryset.update(is_active=True)
        self.message_user(request, f"{rows_updated}位客服可上岗")

    set_service_active.short_description = "设置为“活跃客服”"

    actions = [set_service_active, set_service_inactive]


class EmailVerifyAdmin(admin.ModelAdmin):
    """邮箱验证管理"""
    list_per_page = 30
    list_display = ['email_addr', 'verify_code', 'send_time', "aim"]
    search_fields = ['email_addr', 'verify_code']
    list_display_links = ['email_addr', 'verify_code']
    actions_on_top = True

    def delete(self, request, queryset):
        rows_delete = queryset.delete()
        self.message_user(request, f"{rows_delete[0]}条数据被删除。")

    delete.short_description = "删除选中的 验证信息"
    actions = [delete]


admin.site.register(User, UserAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(EmailVerify, EmailVerifyAdmin)

admin.site.site_title = "MyHouse智能家居后台管理"
admin.site.site_header = "MyHouse智能家居后台管理"
