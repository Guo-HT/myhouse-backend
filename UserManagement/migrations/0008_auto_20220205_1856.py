# Generated by Django 2.1.15 on 2022-02-05 18:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('UserManagement', '0007_service'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': '普通用户', 'verbose_name_plural': '普通用户'},
        ),
    ]