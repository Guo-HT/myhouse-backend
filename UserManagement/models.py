from django.db import models
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.html import format_html
from MyHouse import settings
from django.contrib.auth.hashers import make_password


# Create your models here.
# 用户信息
class User(models.Model):
    """用户名、密码、邮箱、头像、注册时间、是否活跃（注销）"""
    name = models.CharField(max_length=16, verbose_name="用户名")
    passwd = models.CharField(max_length=255, verbose_name="密码")
    email = models.EmailField(unique=True, default="", verbose_name="邮箱")
    head_photo = models.ImageField(upload_to="head_photo/", blank=True, null=True, default="head_photo/defaultHead.png",  verbose_name="头像")
    reg_time = models.DateTimeField(auto_now_add=True, verbose_name="注册时间")
    is_active = models.BooleanField(default=True, verbose_name="有效用户")

    class Meta:
        db_table = "user_info"  # 表名
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.name

    def head_photo_show(self):
        return format_html('<img src="{}{}" alt="" width="24"/>', settings.MEDIA_URL, self.head_photo)  # 在后台管理列表显示图标

    head_photo_show.short_description = "头像"

    def save(self, *args, **kwargs):
        """重写model的save方法"""
        self.passwd = make_password(self.passwd, None, 'pbkdf2_sha256')
        super(User, self).save(*args, **kwargs)


# 客服
class Service(models.Model):
    """用户名、密码、邮箱、头像、注册时间、是否活跃（注销）"""
    name = models.CharField(max_length=16, verbose_name="用户名")
    passwd = models.CharField(max_length=255, verbose_name="密码")
    email = models.EmailField(unique=True, default="", verbose_name="邮箱")
    reg_time = models.DateTimeField(auto_now_add=True, verbose_name="注册时间")
    is_active = models.BooleanField(default=True, verbose_name="有效")

    class Meta:
        db_table = "service_info"  # 表名
        verbose_name = '客服'
        verbose_name_plural = '客服'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """重写model的save方法"""
        self.passwd = make_password(self.passwd, None, 'pbkdf2_sha256')
        super(Service, self).save(*args, **kwargs)


# 邮箱验证
class EmailVerify(models.Model):
    email_addr = models.EmailField(default='', verbose_name="邮箱地址")  # 邮箱目的地址
    verify_code = models.CharField(max_length=6, verbose_name="验证码")  # 发送的验证码
    send_time = models.DateTimeField(auto_now_add=True, verbose_name="发送时间")  # 发送的时间
    aim = models.CharField(max_length=20, default="r", choices=[("r", "用户注册"), ("c", "密码修改")], verbose_name="用途")

    class Meta:
        db_table = "email_verify"
        verbose_name = '邮箱验证'
        verbose_name_plural = '邮箱验证'

    def __str__(self):
        return self.email_addr
