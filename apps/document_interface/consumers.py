'''
Convochat: Chat consumer for real-time interaction with LLM
'''

import json
from asgiref.sync import sync_to_async
import aiohttp
import requests
from langchain_core.messages import HumanMessage, AIMessage
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from django.conf import settings

from . import configure_llm
from .models import Conversation, Message
# from .services import MultiModalHandler
# from .tasks import process_ai_response, process_user_message

# Title generation API
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_TOKEN}"}


async def generate_title(conversation_content):
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, headers=headers, json={"inputs": conversation_content, "parameters": {"max_length": 50, "min_length": 10}}) as response:
            result = await response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0]['summary_text']
            else:
                return "Untitled Conversation"


async def update_conversation_title(conversation, new_title):
    conversation.title = new_title
    await database_sync_to_async(conversation.save)()


async def get_conversation_content(conversation_id, message_limit=5):
    messages = await database_sync_to_async(lambda: list(Message.objects.filter(conversation_id=conversation_id).order_by('-created')[:message_limit]))()
    return " ".join([msg.content for msg in reversed(messages)])


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
        data = json.loads(text_data)
        fe_message = data.get('message')    # front-end message
        uuid = data.get('uuid')

        conversation = await self.get_or_create_conversation(uuid)
        user_message = await self.save_message(conversation, fe_message, is_from_user=True)

        await self.process_response(fe_message, conversation, user_message)

    async def process_response(self, fe_message, conversation, user_message):
        try:
            history = await get_conversation_history(conversation.id)
            history_str = '\n'.join(
                [f"{'Human' if isinstance(msg, HumanMessage) else 'AI'}:{msg.content}" for msg in history]
            )
            input_with_history = {
                'history': history_str,
                'input': fe_message
            }

            # Generate AI response
            llm_response_chunks = []
            async for chunk in configure_llm.chain.astream_events(input_with_history, version='v2', include_names=['Assistant']):
                if chunk['event'] in ['on_parser_start', 'on_parser_stream']:
                    await self.send(text_data=json.dumps(chunk))

                if chunk.get('event') == 'on_parser_end':
                    output = chunk.get('data', {}).get('output', '')
                    llm_response_chunks.append(output)

            ai_response = ''.join(llm_response_chunks)

            # Generate and update title
            if conversation.title == 'Untitled Conversation' or conversation.title is None:
                conversation_content = await get_conversation_content(conversation.id)
                new_title = await generate_title(conversation_content)
                await update_conversation_title(conversation, new_title)
                await self.send(text_data=json.dumps({
                    'type': 'title_update',
                    'title': new_title
                }))

            if not ai_response:
                ai_response = "I apologize, but I couldn't generate a response. Please try asking your question again."

            ai_message = await self.save_message(conversation, ai_response, is_from_user=False, in_reply_to=user_message)

        except Exception as ex:
            print(f"Error during LLM response processing: {ex}")

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
    def save_message(self, conversation, content, is_from_user=True, in_reply_to=None):
        return Message.objects.create(
            conversation=conversation,
            content=content,
            is_from_user=is_from_user,
            in_reply_to=in_reply_to
        )


@database_sync_to_async
def save_conversation_title(conversation, title):
    conversation.title = title
    conversation.save()


@database_sync_to_async
def get_conversation_history(conversation_id, limit=8):
    """Get the last [limit] messages from database 

    Args:
        conversation_id (uuid): the conversation UUID
        limit (int, optional): the number of previous messages. Defaults to 8.

    Returns:
        queryset: last [limit] messages from the conversation
    """
    conversation = Conversation.objects.get(id=conversation_id)
    messages = conversation.messages.order_by('-created')[:limit]
    return [
        HumanMessage(content=msg.content) if msg.is_from_user else AIMessage(
            content=msg.content)
        for msg in reversed(messages)
    ]