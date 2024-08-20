# apps/chat/admin.py

from django.contrib import admin
from .models import Conversation, Message, ChatMessage


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """
    Admin site configuration for Conversation model.
    """
    list_display = ('id', 'title', 'user',
                    'status', 'created')
    list_filter = ('created', 'modified', )
    search_fields = ('user__username', 'title',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Admin site configuration for Message model.
    """
    list_display = ('id', 'conversation',
                    'is_from_user', 'created')
    list_filter = (
        'is_from_user', 'conversation__user__username', 'created')
    ordering = ('-created',)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'message')
