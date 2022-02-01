# Generated by Django 2.1.15 on 2022-01-04 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailVerify',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_addr', models.EmailField(default='', max_length=254, verbose_name='邮箱地址')),
                ('verify_code', models.CharField(max_length=6, verbose_name='验证码')),
                ('send_time', models.DateTimeField(auto_now_add=True, verbose_name='发送时间')),
            ],
            options={
                'verbose_name': '邮箱验证',
                'verbose_name_plural': '邮箱验证',
                'db_table': 'email_verify',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reg_time', models.DateTimeField(auto_created=True, verbose_name='注册时间')),
                ('name', models.CharField(max_length=16, verbose_name='用户名')),
                ('passwd', models.CharField(max_length=255, verbose_name='密码')),
                ('email', models.EmailField(default='', max_length=254, unique=True, verbose_name='邮箱')),
                ('head_photo', models.ImageField(blank=True, default='defaultHead.png', null=True, upload_to='head_photo/', verbose_name='头像')),
            ],
            options={
                'verbose_name': '用户',
                'verbose_name_plural': '用户',
                'db_table': 'user_info',
            },
        ),
    ]
