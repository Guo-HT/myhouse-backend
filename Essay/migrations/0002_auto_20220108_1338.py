# Generated by Django 2.1.15 on 2022-01-08 13:38

import ckeditor_uploader.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('UserManagement', '0005_user_is_active'),
        ('Essay', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EssayComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(max_length=255, verbose_name='评论内容')),
                ('good_num', models.IntegerField(default=0, verbose_name='点赞量')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='发表时间')),
            ],
            options={
                'verbose_name': '文章评论',
                'verbose_name_plural': '文章评论',
                'db_table': 'essay_comment_info',
            },
        ),
        migrations.CreateModel(
            name='EssayCommentReply',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reply', models.TextField(max_length=255, verbose_name='回复')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='发表时间')),
                ('from_comment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Essay.EssayComment', verbose_name='评论')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='UserManagement.User', verbose_name='发表用户')),
            ],
            options={
                'verbose_name': '文章评论回复',
                'verbose_name_plural': '文章评论回复',
                'db_table': 'essay_comment_reply_info',
            },
        ),
        migrations.AlterModelOptions(
            name='essay',
            options={'verbose_name': '文章', 'verbose_name_plural': '文章'},
        ),
        migrations.AlterField(
            model_name='essay',
            name='content',
            field=ckeditor_uploader.fields.RichTextUploadingField(verbose_name='正文内容'),
        ),
        migrations.AddField(
            model_name='essaycomment',
            name='from_essay',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Essay.Essay', verbose_name='文章'),
        ),
        migrations.AddField(
            model_name='essaycomment',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='UserManagement.User', verbose_name='发表用户'),
        ),
    ]
