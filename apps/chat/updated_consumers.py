# apps/chat/consumers.py
import json
import os
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

API_URL = "https://api-inference.huggingface.co/models/czearing/article-title-generator"
headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_TOKEN}"}


async def generate_title(payload):
    response = await sync_to_async(requests.post)(API_URL, headers=headers, json=payload)
    return (await sync_to_async(response.json)())[0]['generated_text']


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
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
        data = json.loads(text_data)
        content_type = data.get('type')
        content = data.get('content')
        uuid = data.get('uuid')

        if not content_type:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Content type not specified'
            }))
            return

        conversation = await self.get_or_create_conversation(uuid)

        if content_type == 'TE':
            user_message = await self.save_message(conversation, content, content_type, is_from_user=True)
        elif content_type in ['IM', 'AU']:
            try:
                file_data = content.split(',')[1]
                file_bytes = base64.b64decode(file_data)
                file_extension = 'png' if content_type == 'IM' else 'mp3'
                file_name = f"user_upload_{uuid}.{file_extension}"

                user_message = await self.save_message(
                    conversation=conversation,
                    content=f"User uploaded a {'image' if content_type == 'IM' else 'audio'} file",
                    content_type=content_type,
                    is_from_user=True,
                    file_content=ContentFile(file_bytes, name=file_name)
                )

                analysis_result = await self.multimodal_handler.process_message(user_message)
                await self.send(text_data=json.dumps({
                    'type': 'analysis_result',
                    'result': analysis_result
                }))
            except Exception as e:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Error processing file: {str(e)}'
                }))
                return
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Unsupported content type: {content_type}'
            }))
            return

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
                    await self.send(text_data=json.dumps({
                        'type': 'ai_response_chunk',
                        'chunk': chunk.get('data', {}).get('output', '')
                    }))

                if chunk.get('event') == 'on_parser_end':
                    output = chunk.get('data', {}).get('output', '')
                    llm_response_chunks.append(output)

            ai_response = ''.join(llm_response_chunks)

            # Generate title if needed
            if conversation.title == 'Untitled Conversation' or conversation.title is None:
                try:
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
                try:
                    audio_file_name = f'ai_response_{ai_message.id}.mp3'
                    audio_file_path = os.path.join(
                        settings.MEDIA_ROOT, 'ai_responses', audio_file_name)
                    os.makedirs(os.path.dirname(
                        audio_file_path), exist_ok=True)
                    await self.multimodal_handler.text_to_speech(ai_response, audio_file_path)
                    await self.send(text_data=json.dumps({
                        'type': 'audio_response',
                        'audio_url': f'/media/ai_responses/{audio_file_name}'
                    }))
                except Exception as ex:
                    print(f"Error generating audio: {ex}")

            await self.send(text_data=json.dumps({
                'type': 'ai_response_end',
                'message': ai_response
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
                id=uuid).update(status='EN')
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
    conversation = Conversation.objects.get(id=conversation_id)
    messages = conversation.messages.order_by('-created')[:limit]
    return [
        HumanMessage(content=msg.content) if msg.is_from_user else AIMessage(
            content=msg.content)
        for msg in reversed(messages)
    ]
