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
    search_fields = ["machine__machine_name__icontains", "data"]
    list_display_links = ["id", "machine", "data"]

    def delete_data(self, request, queryset):
        rows_delete = queryset.delete()
        self.message_user(request, f"{rows_delete[0]}条数据被删除。")

    delete_data.short_description = "删除选中的 硬件数据"

    # actions = [delete_data]


class CommandHistoryAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ["id", "machine", "command", "time"]
    search_fields = ["machine__machine_name__icontains", "command"]
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
    search_fields = ["text", "user__name__icontains", "service__name__icontains"]
    list_display_links = ["id", "text", "user", "service"]

    def delete_data(self, request, queryset):
        rows_delete = queryset.delete()
        self.message_user(request, f"{rows_delete[0]}条数据被删除。")

    delete_data.short_description = "删除选中的 聊天记录"


class MachineLinkAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ["id", "upper", "data_item", "condition", "condition_num", "lower", "command", "command_num"]
    list_filter = ["data_item"]
    search_fields = ["id", "upper__machine_name__icontains", "lower__machine_name__icontains", "data_item"]
    list_display_links = ["id", "upper", "data_item", "condition", "condition_num", "lower", "command", "command_num"]

    def delete_data(self, request, queryset):
        rows_delete = queryset.delete()
        self.message_user(request, f"{rows_delete[0]}条数据被删除。")

    delete_data.short_description = "删除选中的 联动关系"


admin.site.register(Machine, MachineAdmin)
admin.site.register(MachineData, MachineDataAdmin)
admin.site.register(CommandHistory, CommandHistoryAdmin)
admin.site.register(ChatHistory, ChatHistoryAdmin)
admin.site.register(MachineLink, MachineLinkAdmin)
