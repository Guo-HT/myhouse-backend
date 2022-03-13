from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt

from Data import views


# /data/*
urlpatterns = [
    re_path("^test", views.test, name="test"),  # 状态测试接口
    re_path("^machine", views.Machines.as_view(), name="bind"),  # 设备绑定用户
    re_path("^status", views.status, name="bind"),  # 设备绑定用户
    re_path("^get_data", views.get_data, name="get_data"),  # 获取单设备数据
    re_path("^get_machines_data", views.get_machines_data, name="get_machines_data"),  # 获取设备状态
    re_path("^mqtt_ctrl", views.mqtt_ctrl, name="mqtt_ctrl"),  # 控制设备
    re_path("^get_command_history", views.get_command_history, name="get_command_history"),  # 获取硬件指令历史
    re_path("^cut_bind", views.cut_bind, name="cut_bind"),  # 解除绑定
    re_path("^chat_file", csrf_exempt(views.chat_file), name="chat_file"),  # 聊天发送文件
    re_path("^get_chat_history", views.get_chat_history, name="get_chat_history"),  # 获取聊天历史
    re_path("^get_machine_link", views.GetMachineLink.as_view(), name="get_machine_link"),  # 获取设备联动
    re_path("^delete_link", views.machine_link_delete, name="machine_link_delete"),
    re_path("^server_status_data", views.server_status_data, name="server_status_data"),
    re_path("^server_status_info", views.server_status_info, name="server_status_info"),
    re_path("^wstest", views.wstest),  # websocket--即时通信
    re_path("^ip_ban", views.ip_banned),  # 禁用ip
]
