# apps/chat/apis.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .services import MultiModalHandler


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    def get_queryset(self):
        return Message.objects.filter(conversation__user=self.request.user)

    def perform_create(self, serializer):
        file = self.request.data.get('file')
        content_type = 'TE'
        if file:
            if file.content_type.startswith('image'):
                content_type = 'IM'
            elif file.content_type.startswith('audio'):
                content_type = 'AU'
            elif file.content_type.startswith('video'):
                content_type = 'VI'

        message = serializer.save(
            conversation_id=self.request.data.get('conversation'),
            content_type=content_type,
            file_content=file
        )

        if content_type != 'TE':
            multimodal_handler = MultiModalHandler()
            analysis_result = multimodal_handler.process_message(message)
            # Add the analysis result to the response if needed
