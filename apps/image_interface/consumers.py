import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from langchain_core.messages import HumanMessage, AIMessage
from channels.db import database_sync_to_async
from django.core.files.base import ContentFile

from chat.models import Conversation, Message
from chat import configure_llm
from .models import ImageMessage
from .services import ImageModalHandler


class ImageChatConsumer(AsyncWebsocketConsumer):
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
            'message': f"Welcome, {self.user}! You are now connected to the image chat."
        }))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        message_content = data.get('message')
        conversation_id = data.get('uuid')

        conversation = await self.get_or_create_conversation(conversation_id)

        await self.handle_image_message(conversation, message_content)

    async def handle_image_message(self, conversation, image_data):
        voice_handler = VoiceModalHandler()

        # Decode base64 audio data
        image_content = base64.b64decode(image_data)

        # Save user's image message
        user_message = await self.save_message(conversation, 'IM', is_from_user=True)
        await self.save_image_message(user_message, audio_content)

        # Process user audio (speech-to-text)
        text_content = await voice_handler.process_audio(user_message)

        # Send transcription to the client
        await self.send(text_data=json.dumps({
            'type': 'transcription',
            'message': text_content,
            'id': str(user_message.id)
        }))

        # Generate AI response
        ai_response = await self.generate_ai_response(conversation, text_content)

        # Save AI's audio message
        ai_message = await self.save_message(conversation, 'AU', is_from_user=False)
        await self.save_image_message(ai_message, ai_response)

        # Send AI response to the client
        await self.send(text_data=json.dumps({
            'type': 'ai_response',
            'message': ai_response,
            'audio_url': ai_message.audio_content.audio_file.url,
            'id': str(ai_message.id)
        }))

    async def generate_ai_response(self, conversation, input_text):
        history = await get_conversation_history(conversation.id)
        history_str = '\n'.join(
            [f"{'Human' if isinstance(msg, HumanMessage) else 'AI'}:{msg.content}" for msg in history]
        )

        input_with_history = {
            'history': history_str,
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
    def save_message(self, conversation, content_type, is_from_user=True):
        return Message.objects.create(
            conversation=conversation,
            content_type=content_type,
            is_from_user=is_from_user
        )

    @database_sync_to_async
    def save_image_message(self, message, image_content, width, height, description=''):
        image = ContentFile(image_content, name=f"image_{message.id}.png")
        return ImageMessage.objects.create(
            message=message,
            image=image,
            width=width,
            height=height,
            description=description,
        )

    @database_sync_to_async
    def save_chat_message(self, message, content):
        return message.chat_content.create(content=content)

    @database_sync_to_async
    def update_image_message(self, image_message, description):
        image_message.description = description
        image_message.save()


@database_sync_to_async
def get_conversation_history(conversation_id, limit=8):
    conversation = Conversation.objects.get(id=conversation_id)
    messages = conversation.messages.order_by('-created')[:limit]
    return [
        HumanMessage(content=msg.image_content.description) if msg.is_from_user else AIMessage(
            content=msg.image_content.description)
        for msg in reversed(messages)
    ]
