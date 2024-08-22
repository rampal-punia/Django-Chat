import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist

from chat.models import Conversation, Message
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

        if message_type == 'DO':
            await self.handle_document_message(conversation, message_content)
        elif message_type == 'TE':
            await self.handle_text_message(conversation, message_content)

    async def handle_document_message(self, conversation, document_data):
        try:
            document_handler = DocumentModalHandler()

            # Process document
            num_chunks, summary, chunks, embeddings, metadata = await document_handler.process_document(document_data)

            # Save user's document message
            user_message = await self.save_message(conversation, 'DO', is_from_user=True)
            await document_handler.save_document_message(user_message, document_data, num_chunks, summary, chunks, embeddings, metadata)

            # Send document summary to the client
            await self.send(text_data=json.dumps({
                'type': 'document_summary',
                'message': summary,
            }))

            # Update conversation title
            new_title = f"Document Chat: {metadata.get('title', 'Untitled')[:30]}"
            await self.update_conversation_title(conversation, new_title)

        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f"Error processing document: {str(e)}",
            }))

    async def handle_text_message(self, conversation, message_content):
        try:
            document_handler = DocumentModalHandler()

            # Get the latest document message for this conversation
            document_message = await self.get_latest_document_message(conversation)

            # Query the document
            context = await document_handler.query_document(message_content, document_message.id)

            # Generate AI response
            ai_response = await self.generate_ai_response(context, message_content)

            # Save user's text message
            user_message = await self.save_message(conversation, 'TE', is_from_user=True)
            await self.save_chat_message(user_message, message_content)

            # Save AI's text message
            ai_message = await self.save_message(conversation, 'TE', is_from_user=False)
            await self.save_chat_message(ai_message, ai_response)

            # Send AI response to the client
            await self.send(text_data=json.dumps({
                'type': 'ai_response',
                'message': ai_response,
            }))

        except ObjectDoesNotExist:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': "No document has been uploaded for this conversation. Please upload a document first.",
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f"Error processing your question: {str(e)}",
            }))

    async def generate_ai_response(self, context, query):
        prompt = f"""You are an AI assistant helping to answer questions based on a given document. 
        Use the following context to answer the user's question. If you cannot answer the question based on the context, 
        say that you don't have enough information to answer accurately.

        Context: {context}

        User Question: {query}

        Answer:"""

        response = await configure_llm.chain.ainvoke({"input": prompt})
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
    def save_chat_message(self, message, content):
        return message.chat_content.create(content=content)

    @database_sync_to_async
    def get_latest_document_message(self, conversation):
        return DocumentMessage.objects.filter(message__conversation=conversation).latest('message__created')

    @database_sync_to_async
    def update_conversation_title(self, conversation, new_title):
        conversation.title = new_title
        conversation.save()
        return conversation
