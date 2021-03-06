# Generated by Django 2.1.15 on 2022-01-31 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserManagement', '0006_auto_20220119_1539'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16, verbose_name='用户名')),
                ('passwd', models.CharField(max_length=255, verbose_name='密码')),
                ('email', models.EmailField(default='', max_length=254, unique=True, verbose_name='邮箱')),
                ('reg_time', models.DateTimeField(auto_now_add=True, verbose_name='注册时间')),
                ('is_active', models.BooleanField(default=True, verbose_name='有效')),
            ],
            options={
                'verbose_name': '客服',
                'verbose_name_plural': '客服',
                'db_table': 'service_info',
            },
        ),
    ]
