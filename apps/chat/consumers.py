# apps/chat/consumers.py

import json
import base64
from django.core.files.base import ContentFile
from asgiref.sync import sync_to_async

import requests
from langchain_core.messages import HumanMessage, AIMessage
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from django.conf import settings

from . import configure_llm
from .models import Conversation, Message
from .services import MultiModalHandler
# from .tasks import process_ai_response, process_user_message

# Title generation API
API_URL = "https://api-inference.huggingface.co/models/czearing/article-title-generator"
headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_TOKEN}"}


async def generate_title(payload):
    response = await sync_to_async(requests.post)(API_URL, headers=headers, json=payload)
    return (await sync_to_async(response.json)())[0]['generated_text']


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

        self.multimodal_handler = MultiModalHandler()

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
        # content = data.get('message')    # front-end message
        content_type = data.get('type', 'TE')
        content = data.get('content')
        uuid = data.get('uuid')

        conversation = await self.get_or_create_conversation(uuid)
        if content_type == 'TE':
            user_message = await self.save_message(
                conversation,
                content,
                content_type,
                is_from_user=True
            )
        elif content_type != ['IM', 'AU']:
            user_message = await self.save_message(
                conversation=conversation,
                content=f"User uploaded a {'image' if content_type == 'IM' else 'audio'} file",
                content_type=content_type,
                file=content,
                is_from_user=True
            )
            analysis_result = await self.multimodal_handler.process_message(user_message)
            await self.send(text_data=json.dumps({
                'type': 'analysis_result',
                'result': analysis_result
            }))

        await self.process_response(content, conversation, user_message)

    async def process_response(self, content, conversation, user_message):
        try:
            history = await get_conversation_history(conversation.id)
            history_str = '\n'.join(
                [f"{'Human' if isinstance(msg, HumanMessage) else 'AI'}:{msg.content}" for msg in history]
            )
            input_with_history = {
                'history': history_str,
                'input': content
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

            # Generate title if needed
            try:
                if conversation.title == 'Untitled Conversation' or conversation.title is None:
                    title = await generate_title(ai_response)
                    await save_conversation_title(conversation, title)
                    await self.send(text_data=json.dumps({
                        'type': 'title',
                        'message': title
                    }))
            except Exception as ex:
                print(f"Unable to generate title: {ex}")

            if not ai_response:
                ai_response = "I apologize, but I couldn't generate a response. Please try asking your question again."

            ai_message = await self.save_message(conversation, ai_response, is_from_user=False, in_reply_to=user_message)

            if user_message.content_type != 'TE':
                # Generate speech from the AI response
                audio_file = self.multimodal_handler.text_to_speech(
                    ai_response, f'ai_response_{ai_message.id}.mp3')

            await self.send(text_data=json.dumps({
                'type': 'ai_response',
                'message': ai_response,
                'audio_url': f'/media/ai_responses/ai_response_{ai_message.id}.mp3'
            }))
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
    def save_message(self, conversation, content, content_type='TE', is_from_user=True, in_reply_to=None, file_content=None):
        msg = Message.objects.create(
            conversation=conversation,
            content=content,
            content_type=content_type,
            is_from_user=is_from_user,
            in_reply_to=in_reply_to
        )
        if file_content:
            msg.file.save(file_content.name, file_content, save=True)

        return msg


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
