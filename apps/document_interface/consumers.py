import json
import asyncio
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from django.core.exceptions import ObjectDoesNotExist

from chat.models import Conversation, Message, ChatMessage
from .models import DocumentMessage
from .services import DocumentModalHandler
from common.text_chat_handler import TextChatHandler


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

        if message_type == 'DO':
            await self.handle_document_message(conversation, message_content)
        elif message_type == 'TE':
            await self.handle_text_message(conversation, message_content)

    async def handle_document_message(self, conversation, document_data):
        # try:
        document_handler = DocumentModalHandler()

        # Process document
        num_chunks, summary, chunks, embeddings, metadata, document_hash = await document_handler.process_document(document_data)

        # Check if this is an existing document
        self.document_message = await document_handler.get_existing_document(document_hash)

        if self.document_message:
            # If the document already exists, we don't need to save it again
            await self.send(text_data=json.dumps({
                'type': 'document_summary',
                'message': self.document_message.summary,
            }))

            # Update conversation title
            # new_title = await self.get_title_from_metadata(existing_document.metadata)
            # await self.update_conversation_title(conversation, new_title)
        else:
            # Save user's document message
            user_message = await self.save_message(conversation, 'DO', is_from_user=True)
            self.document_message = await document_handler.save_document_message(user_message, document_data, num_chunks, summary, chunks, embeddings, metadata, document_hash)

            # Send document summary to the client
            await self.send(text_data=json.dumps({
                'type': 'document_summary',
                'message': summary,
            }))

            # Update conversation title
            new_title = await self.get_title_from_metadata(metadata)
            await self.update_conversation_title(conversation, new_title)

        # except Exception as e:
        #     await self.send(text_data=json.dumps({
        #         'type': 'error',
        #         'message': f"Error processing document: {str(e)}",
        #     }))

    async def handle_text_message(self, conversation, message_content):

        # Save user's text message
        user_message = await self.save_message(conversation, 'TE', is_from_user=True)
        await self.save_chat_message(user_message, message_content)

        # try:
        document_handler = DocumentModalHandler()

        # Query the document
        context = await document_handler.query_document(message_content, self.document_message.id)

        # Generate AI response
        await TextChatHandler.process_text_response(
            conversation,
            user_message,
            message_content,
            self.send,
            context,
            self.document_message.summary
        )

        # except ObjectDoesNotExist:
        #     await self.send(text_data=json.dumps({
        #         'type': 'error',
        #         'message': "No document has been uploaded for this conversation. Please upload a document first.",
        #     }))
        # except Exception as e:
        #     await self.send(text_data=json.dumps({
        #         'type': 'error',
        #         'message': f"Error processing your question: {str(e)}",
        #     }))

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
    def save_chat_message(self, message, content):
        return ChatMessage.objects.create(
            message=message,
            content=content
        )

    @database_sync_to_async
    def get_latest_document_message(self, conversation):
        return DocumentMessage.objects.filter(message__conversation=conversation).latest('message__created')

    @database_sync_to_async
    def update_conversation_title(self, conversation, new_title):
        conversation.title = new_title
        conversation.save()
        return conversation

    @sync_to_async
    def get_title_from_metadata(self, metadata):
        title = metadata.get('title', 'Untitled') if isinstance(
            metadata, dict) else getattr(metadata, 'title', 'Untitled')
        return f"Document Chat: {title[:30]}"

    @database_sync_to_async
    def update_conversation_title(self, conversation, new_title):
        conversation.title = new_title
        conversation.save()
        return conversation
