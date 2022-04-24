from django.db import models
from UserManagement.models import User


# Create your models here.
class Machine(models.Model):
    WORK_TYPE = (  # 编码：功能
        ("1", "light"),
        ("2", "dht11"),
    )
    mac_addr = models.CharField(max_length=20, unique=True, verbose_name="MAC地址")
    user_belong = models.ForeignKey("UserManagement.User", null=True, blank=True, on_delete=models.CASCADE, db_constraint=False, verbose_name="从属用户") # 逻辑外键
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
    machine = models.ForeignKey("Machine", blank=False, null=False, on_delete=models.CASCADE, db_constraint=False, verbose_name="设备") # 逻辑外键
    data = models.CharField(max_length=200, verbose_name="设备数据")
    upload_time = models.CharField(max_length=100, verbose_name="设备采集时间")

    class Meta:
        db_table = "machine_data"
        verbose_name = "设备数据"
        verbose_name_plural = "设备数据"

    def __str__(self):
        return self.data


class CommandHistory(models.Model):
    machine = models.ForeignKey("Machine", blank=False, null=False, on_delete=models.CASCADE, db_constraint=False, verbose_name="设备") # 逻辑外键
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
    user = models.ForeignKey("UserManagement.User", default="", on_delete=models.CASCADE, db_constraint=False, verbose_name="用户") # 逻辑外键
    service = models.ForeignKey("UserManagement.Service", default="", on_delete=models.CASCADE, db_constraint=False, verbose_name="客服") # 逻辑外键
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


class MachineLink(models.Model):
    upper = models.ForeignKey("Machine", on_delete=models.CASCADE, related_name="upper", db_constraint=False, verbose_name="上位机") # 逻辑外键
    lower = models.ForeignKey("Machine", on_delete=models.CASCADE, related_name="lower", db_constraint=False, verbose_name="下位机") # 逻辑外键
    data_item = models.TextField(max_length=24, default="", verbose_name="数据项")
    condition = models.CharField(max_length=10, default="", verbose_name="触发条件")  # eq\lt\gt
    condition_num = models.IntegerField(default=0, verbose_name="触发阈值")
    command = models.CharField(max_length=10, default="", verbose_name="设备命令")
    command_num = models.IntegerField(default=0, verbose_name="执行幅度")

    class Meta:
        db_table = "machine_link"
        verbose_name = "设备联动"
        verbose_name_plural = "设备联动"

    def __str__(self):
        return self.upper.machine_name + "->" + self.lower.machine_name


class BanIp(models.Model):
    ip_addr = models.CharField(max_length=16, default="", unique=True, verbose_name="IP地址")
    times = models.IntegerField(default=0, verbose_name="次数")
    last_time = models.DateTimeField(auto_now=True, verbose_name="最近一次时间")

    def __str__(self):
        return self.ip_addr

    class Meta:
        db_table="ip_banned"
        verbose_name = "IP黑名单"
        verbose_name_plural = "IP黑名单"
