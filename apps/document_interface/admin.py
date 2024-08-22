from django.contrib import admin
from .models import DocumentMessage, DocumentChunk, DocumentMetadata


@admin.register(DocumentMessage)
class DocumentMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'message')


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ('id', )


@admin.register(DocumentMetadata)
class DocumentMetadataAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'page_count')
