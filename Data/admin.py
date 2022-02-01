from django.contrib import admin
from Data.models import *


# Register your models here.
class MachineAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ["id", "mac_addr", "user_belong", "machine_name", "work_type", "is_online"]
    list_filter = ["is_online", "work_type"]
    search_fields = ["mac_addr", "machine_name"]
    list_display_links = ["id", "mac_addr", "user_belong", "machine_name"]


class MachineDataAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ["id", "machine", "data", "upload_time"]
    search_fields = ["machine", "data"]
    list_display_links = ["id", "machine", "data"]

    def delete_data(self, request, queryset):
        rows_delete = queryset.delete()
        self.message_user(request, f"{rows_delete[0]}条数据被删除。")

    delete_data.short_description = "删除选中的 硬件数据"

    # actions = [delete_data]


class CommandHistoryAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ["id", "machine", "command", "time"]
    search_fields = ["machine", "command"]
    list_display_links = ["id", "machine", "command"]

    def delete_data(self, request, queryset):
        rows_delete = queryset.delete()
        self.message_user(request, f"{rows_delete[0]}条数据被删除。")

    delete_data.short_description = "删除选中的 指令数据"

    # actions = [delete_data]


class ChatHistoryAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ["id", "text", "user", "service", "time", "content_type", "from_type"]
    list_filter = ["content_type", "from_type"]
    search_fields = ["text", "user", "service"]
    list_display_links = ["id", "text", "user", "service"]

    def delete_data(self, request, queryset):
        rows_delete = queryset.delete()
        self.message_user(request, f"{rows_delete[0]}条数据被删除。")

    delete_data.short_description = "删除选中的 聊天记录"


admin.site.register(Machine, MachineAdmin)
admin.site.register(MachineData, MachineDataAdmin)
admin.site.register(CommandHistory, CommandHistoryAdmin)
admin.site.register(ChatHistory, ChatHistoryAdmin)


"""
list_per_page = 20
list_display = []
list_filter = []
search_fields = []
list_display_links = []
"""
