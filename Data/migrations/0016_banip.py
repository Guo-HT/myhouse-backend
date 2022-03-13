# Generated by Django 2.2 on 2022-03-13 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Data', '0015_chathistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='BanIp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_addr', models.CharField(default='', max_length=16, unique=True, verbose_name='IP地址')),
                ('times', models.IntegerField(default=0, verbose_name='次数')),
                ('last_time', models.DateTimeField(auto_now=True, verbose_name='最近一次时间')),
            ],
            options={
                'verbose_name': 'IP黑名单',
                'verbose_name_plural': 'IP黑名单',
                'db_table': 'ip_banned',
            },
        ),
    ]
