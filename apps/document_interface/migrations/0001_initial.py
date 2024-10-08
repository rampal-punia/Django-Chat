# Generated by Django 5.0.8 on 2024-08-22 11:11

import django.db.models.deletion
import document_interface.models
import pgvector.django
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('chat', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.FileField(upload_to='document_messages/', validators=[document_interface.models.validate_pdf])),
                ('num_pages', models.IntegerField()),
                ('num_chunks', models.IntegerField()),
                ('file_type', models.CharField(max_length=255)),
                ('processed_content', models.TextField(blank=True)),
                ('summary', models.TextField(blank=True)),
                ('message', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='document_content', to='chat.message')),
            ],
        ),
        migrations.CreateModel(
            name='DocumentChunk',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('embedding', pgvector.django.VectorField(dimensions=768)),
                ('metadata', models.JSONField(default=dict)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chunks', to='document_interface.documentmessage')),
            ],
        ),
        migrations.CreateModel(
            name='DocumentMetadata',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255)),
                ('author', models.CharField(blank=True, max_length=255)),
                ('creation_date', models.DateTimeField(blank=True, null=True)),
                ('last_modified_date', models.DateTimeField(blank=True, null=True)),
                ('page_count', models.IntegerField(null=True)),
                ('word_count', models.IntegerField(null=True)),
                ('document', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='metadata', to='document_interface.documentmessage')),
            ],
        ),
    ]
