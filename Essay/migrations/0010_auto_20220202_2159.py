# Generated by Django 2.1.15 on 2022-02-02 21:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Essay', '0009_essaycollection'),
    ]

    operations = [
        migrations.AlterField(
            model_name='essaycommentreply',
            name='reply_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reply_to', to='UserManagement.User', verbose_name='回复谁'),
        ),
    ]
