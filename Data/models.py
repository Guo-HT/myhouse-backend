from django.db import models
from UserManagement.models import User


# Create your models here.
class Machine(models.Model):
    WORK_TYPE = (  # 编码：功能
        ("1", "light"),
        ("2", "dht11"),
    )
    mac_addr = models.CharField(max_length=20, unique=True, verbose_name="MAC地址")
    user_belong = models.ForeignKey("UserManagement.User", null=True, blank=True, on_delete=models.CASCADE, verbose_name="从属用户")
    is_online = models.BooleanField(default=False, verbose_name="是否在线")
    work_type = models.CharField(max_length=10, default="", choices=WORK_TYPE, verbose_name="设备类型")
    machine_name = models.CharField(max_length=20, default="我的设备", verbose_name="设备名称")

    class Meta:
        db_table = "machine_info"
        verbose_name = "硬件设备"
        verbose_name_plural = "硬件设备"

    def __str__(self):
        return self.mac_addr


class MachineData(models.Model):
    machine = models.ForeignKey("Machine", blank=False, null=False, on_delete=models.CASCADE, verbose_name="设备")
    data = models.CharField(max_length=200, verbose_name="设备数据")
    upload_time = models.CharField(max_length=100, verbose_name="设备采集时间")

    class Meta:
        db_table = "machine_data"
        verbose_name = "设备数据"
        verbose_name_plural = "设备数据"

    def __str__(self):
        return self.data


class CommandHistory(models.Model):
    machine = models.ForeignKey("Machine", blank=False, null=False, on_delete=models.CASCADE, verbose_name="设备")
    time = models.DateTimeField(auto_now_add=True, verbose_name="发送时间")
    command = models.CharField(max_length=20, default="", verbose_name="指令内容")

    class Meta:
        db_table = "machine_command_history"
        verbose_name = "命令历史"
        verbose_name_plural = "命令历史"

    def __str__(self):
        return str(self.machine.machine_name) + "-" + self.command


class ChatHistory(models.Model):
    time = models.CharField(max_length=32, verbose_name="发送时间")
    user = models.ForeignKey("UserManagement.User", default="", on_delete=models.CASCADE, verbose_name="用户")
    service = models.ForeignKey("UserManagement.Service", default="", on_delete=models.CASCADE, verbose_name="客服")
    text = models.TextField(max_length=255, verbose_name="内容")
    content_type = models.CharField(max_length=10, verbose_name="类型")
    from_type = models.TextField(max_length=10, default="", verbose_name="发送方类型")

    class Meta:
        db_table = "chat_history"
        verbose_name = "聊天历史"
        verbose_name_plural = "聊天历史"

    def __str__(self):
        if self.from_type == "user":
            return f"用户:{self.user.name}->客服{self.service.name}:{self.text}"
        elif self.from_type == "service":
            return f"客服{self.service.name}->用户:{self.user.name}:{self.text}"

