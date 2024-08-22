# apps/image_interface/admin.py

from django.contrib import admin
from .models import DocumentMessage


@admin.register(DocumentMessage)
class DocumentMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'message')
