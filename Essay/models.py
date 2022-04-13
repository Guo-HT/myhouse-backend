from django.db import models
from UserManagement.models import User
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField


# Create your models here.
# 文章
class Essay(models.Model):
    title = models.CharField(max_length=50, verbose_name="标题")
    content = RichTextUploadingField(config_name="default", verbose_name="正文内容")  # 富文本编辑器(可以上传图片)
    user = models.ForeignKey("UserManagement.User", blank=True, null=True, on_delete=models.DO_NOTHING, verbose_name="上传用户") #, db_contraint=False
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    watch_num = models.IntegerField(default=0, verbose_name="浏览量")
    is_checked = models.BooleanField(default=True, verbose_name="是否过审")
    is_delete = models.BooleanField(default=False, verbose_name="是否被用户删除")

    class Meta:
        db_table = "essay_info"
        verbose_name = "文章"
        verbose_name_plural = "文章"

    def __str__(self):
        return self.title

    def content_preview(self):
        return self.content[0:10]
    
    content_preview.short_description = "文章内容"

    def user_name(self):
        return self.user.name

    user_name.short_description = "发表用户"


# 文章评论
class EssayComment(models.Model):
    comment = models.TextField(max_length=255, verbose_name="评论内容")
    from_essay = models.ForeignKey("Essay", blank=True, null=True, on_delete=models.CASCADE, verbose_name="文章") # , db_contraint=False
    good_num = models.IntegerField(default=0, verbose_name="点赞量")
    user = models.ForeignKey("UserManagement.User", blank=True, null=True, verbose_name="发表用户", on_delete=models.DO_NOTHING) # , db_contraint=False
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="发表时间")

    class Meta:
        db_table = "essay_comment_info"
        verbose_name = "文章评论"
        verbose_name_plural = "文章评论"

    def __str__(self):
        return self.comment[0:10]


# 文章评论回复
class EssayCommentReply(models.Model):
    reply = models.TextField(max_length=255, verbose_name="回复")
    from_comment = models.ForeignKey("EssayComment", blank=True, null=True, on_delete=models.CASCADE, verbose_name="回复内容") # , db_contraint=False
    reply_to = models.ForeignKey("UserManagement.User", blank=True, null=True, on_delete=models.CASCADE, related_name="reply_to", verbose_name="回复谁") #, db_contraint=False
    user = models.ForeignKey("UserManagement.User", blank=True, null=True, on_delete=models.DO_NOTHING, related_name="reply_from", verbose_name="发表用户") #, db_contraint=False
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="发表时间")
    good_num = models.IntegerField(default=0, verbose_name="点赞量")

    class Meta:
        db_table = "essay_comment_reply_info"
        verbose_name = "文章评论回复"
        verbose_name_plural = "文章评论回复"

    def __str__(self):
        if len(self.reply) <= 10:
            return self.reply
        else:
            return self.reply[:10]


# 点赞记录
class GoodList(models.Model):
    user = models.ForeignKey("UserManagement.User", blank=False, null=False, on_delete=models.CASCADE, verbose_name="点赞用户") # , db_contraint=False
    essay = models.ForeignKey("Essay", blank=False, null=False, on_delete=models.CASCADE, verbose_name="点赞文章") # , db_contraint=False
    time = models.DateTimeField(auto_now_add=True, verbose_name="点赞时间")

    class Meta:
        db_table = "essay_good_list"
        verbose_name = "文章点赞记录"
        verbose_name_plural = "文章点赞记录"

    def __str__(self):
        return self.user.name+"-"+self.essay.title


# 浏览历史
class BrowseHistory(models.Model):
    user = models.ForeignKey("UserManagement.User", blank=True, null=True, on_delete=models.CASCADE, verbose_name="用户") #, db_contraint=False
    essay = models.ForeignKey("Essay", blank=False, null=False, on_delete=models.CASCADE, verbose_name="浏览文章") # , db_contraint=False
    time = models.DateTimeField(auto_now_add=True, verbose_name="浏览时间")
    ip = models.CharField(max_length=25, verbose_name="IP地址")

    class Meta:
        db_table = "essay_browse_history"
        verbose_name = "文章浏览记录"
        verbose_name_plural = "文章浏览记录"

    def __str__(self):
        return self.user.name + "-" + self.essay.title


# 收藏文章
class EssayCollection(models.Model):
    user = models.ForeignKey("UserManagement.User", blank=True, null=True, on_delete=models.CASCADE, verbose_name="用户") # , db_contraint=False
    essay = models.ForeignKey("Essay", blank=False, null=False, on_delete=models.CASCADE, verbose_name="收藏文章") # , db_contraint=False
    time = models.DateTimeField(auto_now_add=True, verbose_name="收藏时间")

    class Meta:
        db_table = "essay_collection"
        verbose_name = "文章收藏记录"
        verbose_name_plural = "文章收藏记录"

    def __str__(self):
        return self.user.name + "-" + self.essay.title

