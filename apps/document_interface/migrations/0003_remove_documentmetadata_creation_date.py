# Generated by Django 5.0.8 on 2024-08-22 13:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document_interface', '0002_alter_documentchunk_embedding'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documentmetadata',
            name='creation_date',
        ),
    ]