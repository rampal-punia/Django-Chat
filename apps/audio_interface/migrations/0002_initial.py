# Generated by Django 5.0.8 on 2024-08-22 09:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('audio_interface', '0001_initial'),
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='audiomessage',
            name='message',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='audio_content', to='chat.message'),
        ),
    ]
