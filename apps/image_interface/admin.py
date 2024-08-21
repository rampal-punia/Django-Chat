# apps/image_interface/admin.py

from django.contrib import admin
from .models import ImageMessage


@admin.register(ImageMessage)
class ImageMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'message')
