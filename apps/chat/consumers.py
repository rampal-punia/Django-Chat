import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import Conversation, Message, ChatMessage
from common.text_chat_handler import TextChatHandler


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        '''Accept the connections from front-end'''
        # get the user from scope
        self.user = self.scope['user']
        # check if the user is authenticated
        if not self.user.is_authenticated:
            await self.close()
            return

        # Get the conversation UUID from the url route
        self.conversation_id = self.scope['url_route']['kwargs'].get(
            'conversation_id')

        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'welcome',
            'message': f"Welcome, {self.user}! you are now connected to the convo-chat."
        }))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None):
        '''Run on receiving text data from front-end.'''
        input_data, conversation, user_message = await self.create_conversation_db(text_data)

        await TextChatHandler.process_text_response(
            conversation,
            user_message,
            input_data,
            self.send
        )

    async def create_conversation_db(self, text_data):
        data = json.loads(text_data)
        input_type = data.get('type')   # front-end message
        input_data = data.get('message')
        uuid = data.get('uuid')

        conversation = await self.get_or_create_conversation(uuid)
        user_message = await self.save_message(conversation, input_type, is_from_user=True)
        await self.save_chat_message(user_message, input_data)
        return input_data, conversation, user_message

    @database_sync_to_async
    def get_or_create_conversation(self, uuid):
        conversation, created = Conversation.objects.update_or_create(
            id=uuid,
            defaults={
                'user': self.user,
                'status': 'AC'
            }
        )
        if created:
            Conversation.objects.filter(user=self.user, status='AC').exclude(
                id=uuid
            ).update(status='EN')
        return conversation

    @database_sync_to_async
    def save_chat_message(self, message, input_data):
        return ChatMessage.objects.create(
            message=message,
            content=input_data,
        )

    @database_sync_to_async
    def save_message(self, conversation, content_type, is_from_user=True, in_reply_to=None):
        return Message.objects.create(
            conversation=conversation,
            content_type=content_type,
            is_from_user=is_from_user,
            in_reply_to=in_reply_to
        )
