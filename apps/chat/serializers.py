# apps/chat/serializers.py

from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'content', 'is_from_user', 'created', 'modified']


class ConversationSerializer(serializers.ModelSerializer):
    message = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'title', 'status', 'created', 'modified', 'message']
