# Generated by Django 2.1.15 on 2022-01-08 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserManagement', '0004_auto_20220107_1052'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='有效用户'),
        ),
    ]
