# Generated by Django 2.2 on 2022-03-08 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Essay', '0010_auto_20220202_2159'),
    ]

    operations = [
        migrations.AddField(
            model_name='essay',
            name='is_delete',
            field=models.BooleanField(default=False, verbose_name='是否被用户删除'),
        ),
    ]
