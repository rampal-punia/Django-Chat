# Generated by Django 5.0.8 on 2024-08-20 10:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audio_interface', '0001_initial'),
        ('chat', '0008_remove_imageanalysis_message_remove_message_content_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audiomessage',
            name='message',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='audio_content', to='chat.message'),
        ),
    ]