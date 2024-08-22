import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from langchain_core.messages import HumanMessage, AIMessage
from channels.db import database_sync_to_async
from django.core.exceptions import ValidationError

from chat.models import Conversation, Message, ChatMessage
from chat import configure_llm
from .models import DocumentMessage
from .services import DocumentModalHandler


class DocumentChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return

        self.conversation_id = self.scope['url_route']['kwargs'].get(
            'conversation_id')
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'welcome',
            'message': f"Welcome, {self.user}! You are now connected to the Document chat."
        }))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        message_content = data.get('message')
        conversation_id = data.get('uuid')

        conversation = await self.get_or_create_conversation(conversation_id)

        await self.handle_document_message(conversation, message_content)

    async def handle_document_message(self, conversation, document_data):
        document_handler = DocumentModalHandler()

        # Process document
        processed_document, document_description = await document_handler.process_document(document_data)

        # Save user's document message
        user_message = await self.save_message(conversation, 'IM', is_from_user=True)
        img_message = await self.save_document_message(user_message, processed_document, document_description)

        # Send document description(Initial from the document descriptor model) to the client
        await self.send(text_data=json.dumps({
            'type': 'document_description',
            'message': document_description,
            'id': str(user_message.id)
        }))

        # Generate detailed AI response
        ai_response = await self.generate_ai_response(document_description)
        print("AI Response:", ai_response)

        # Save AI's text message
        ai_message = await self.save_message(conversation, 'IM', is_from_user=False, in_reply_to=user_message)
        await self.save_chat_message(ai_message, ai_response)

    async def generate_ai_response(self, input_text):
        input_with_history = {
            'history': 'User is uploading the document and want you to describe it in 100 words based on the description provided.',
            'input': input_text
        }

        response = await configure_llm.chain.ainvoke(input_with_history)
        return response

    @database_sync_to_async
    def get_or_create_conversation(self, conversation_id):
        conversation, created = Conversation.objects.update_or_create(
            id=conversation_id,
            defaults={
                'user': self.user,
                'status': 'AC'
            }
        )
        if created:
            Conversation.objects.filter(user=self.user, status='AC').exclude(
                id=conversation_id).update(status='EN')
        return conversation

    @database_sync_to_async
    def save_message(self, conversation, content_type, is_from_user=True, in_reply_to=None):
        return Message.objects.create(
            conversation=conversation,
            content_type=content_type,
            is_from_user=is_from_user,
            in_reply_to=in_reply_to
        )

    @database_sync_to_async
    def save_document_message(self, message, document_array, description):
        document_message = DocumentMessage.objects.create(
            message=message,
            width=document_array.shape[1],
            height=document_array.shape[0],
            description=description
        )
        DocumentModalHandler.update_document_message(
            document_message, document_array, description)
        return document_message

    @database_sync_to_async
    def save_chat_message(self, message, content):
        return ChatMessage.objects.create(
            message=message,
            content=content,
        )


@database_sync_to_async
def get_conversation_history(conversation_id, limit=8):
    conversation = Conversation.objects.get(id=conversation_id)
    messages = conversation.messages.order_by('-created')[:limit]
    return [
        HumanMessage(content=msg.document_content.description if msg.content_type ==
                     'IM' else msg.chat_content.content)
        if msg.is_from_user
        else AIMessage(content=msg.chat_content.content)
        for msg in reversed(messages)
    ]
