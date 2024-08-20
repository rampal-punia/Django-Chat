# Generated by Django 5.0.7 on 2024-08-19 12:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='content_type',
            field=models.CharField(choices=[('TE', 'Text'), ('IM', 'Image'), ('AU', 'Audio'), ('VI', 'Video')], default='TE', max_length=2),
        ),
        migrations.AddField(
            model_name='message',
            name='file_content',
            field=models.FileField(blank=True, null=True, upload_to='message_files/'),
        ),
        migrations.CreateModel(
            name='AudioAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('analysis_result', models.JSONField()),
                ('message', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='chat.message')),
            ],
        ),
        migrations.CreateModel(
            name='ImageAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('analysis_result', models.JSONField()),
                ('message', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='chat.message')),
            ],
        ),
    ]