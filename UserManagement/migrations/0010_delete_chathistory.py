# Generated by Django 2.2 on 2022-03-12 15:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('UserManagement', '0009_chathistory'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ChatHistory',
        ),
    ]