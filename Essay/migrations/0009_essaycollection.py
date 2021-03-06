# Generated by Django 2.1.15 on 2022-01-22 15:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('UserManagement', '0006_auto_20220119_1539'),
        ('Essay', '0008_auto_20220121_2352'),
    ]

    operations = [
        migrations.CreateModel(
            name='EssayCollection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')),
                ('essay', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Essay.Essay', verbose_name='收藏文章')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='UserManagement.User', verbose_name='用户')),
            ],
            options={
                'verbose_name': '文章收藏记录',
                'verbose_name_plural': '文章收藏记录',
                'db_table': 'essay_collection',
            },
        ),
    ]
