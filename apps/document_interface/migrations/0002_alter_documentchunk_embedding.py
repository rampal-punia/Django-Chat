# Generated by Django 5.0.8 on 2024-08-22 13:12

import pgvector.django
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document_interface', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentchunk',
            name='embedding',
            field=pgvector.django.VectorField(dimensions=384),
        ),
    ]
