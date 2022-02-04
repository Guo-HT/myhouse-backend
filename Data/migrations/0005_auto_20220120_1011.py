# Generated by Django 2.1.15 on 2022-01-20 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Data', '0004_machine_work_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='machine',
            name='cur_status',
        ),
        migrations.AddField(
            model_name='machinedata',
            name='cur_status',
            field=models.CharField(default='', max_length=32, verbose_name='当前状态'),
        ),
    ]