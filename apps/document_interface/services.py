from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import asyncio
import requests
import io
import base64
from django.conf import settings
from .models import DocumentMessage, DocumentChunk, DocumentMetadata
from django.core.files.base import ContentFile
import pypdf
from datetime import datetime

API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_TOKEN}"}


class DocumentModalHandler:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    async def process_document(self, document_content):
        # Save the document content to a temporary file
        temp_file = io.BytesIO(base64.b64decode(document_content))

        # Load the PDF
        loader = PyPDFLoader(temp_file)
        pages = loader.load()

        # Extract metadata
        metadata = await self.extract_metadata(temp_file)

        # Split the document into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_documents(pages)

        # Generate embeddings for chunks
        embeddings = await asyncio.to_thread(self.embeddings.embed_documents, [chunk.page_content for chunk in chunks])

        # Generate summary
        full_text = " ".join([chunk.page_content for chunk in chunks])
        summary = await self.generate_summary_using_LLM(full_text[:4000])

        return len(chunks), summary, chunks, embeddings, metadata

    async def extract_metadata(self, file):
        pdf = pypdf.PdfReader(file)
        info = pdf.metadata
        return {
            'title': info.get('/Title', ''),
            'author': info.get('/Author', ''),
            'creation_date': info.get('/CreationDate', ''),
            'page_count': len(pdf.pages),
            'word_count': sum(len(page.extract_text().split()) for page in pdf.pages)
        }

    async def generate_summary_using_LLM(self, text):
        response = await asyncio.to_thread(
            requests.post,
            API_URL,
            headers=headers,
            json={"inputs": text, "parameters": {
                "max_length": 300, "min_length": 100}}
        )
        return response.json()[0]['summary_text']

    async def query_document(self, query, document_id):
        # Embed the query
        query_embedding = await asyncio.to_thread(self.embeddings.embed_query, query)

        # Retrieve relevant chunks
        chunks = DocumentChunk.objects.filter(document_id=document_id)
        relevant_chunks = sorted(
            chunks,
            key=lambda x: self.cosine_similarity(query_embedding, x.embedding),
            reverse=True
        )[:3]

        context = " ".join([chunk.content for chunk in relevant_chunks])
        return context

    @staticmethod
    def cosine_similarity(v1, v2):
        return sum(a*b for a, b in zip(v1, v2)) / (sum(a*a for a in v1)**0.5 * sum(b*b for b in v2)**0.5)

    @staticmethod
    async def save_document_message(message, document_data, num_chunks, summary, chunks, embeddings, metadata):
        document_content = ContentFile(base64.b64decode(
            document_data), name=f"document_{message.id}.pdf")
        document_message = DocumentMessage.objects.create(
            message=message,
            document=document_content,
            num_pages=metadata['page_count'],
            num_chunks=num_chunks,
            processed_content=" ".join(
                [chunk.page_content for chunk in chunks]),
            summary=summary
        )

        # Save chunks and embeddings
        for chunk, embedding in zip(chunks, embeddings):
            DocumentChunk.objects.create(
                document=document_message,
                content=chunk.page_content,
                embedding=embedding,
                metadata=chunk.metadata
            )

        # Save metadata
        DocumentMetadata.objects.create(
            document=document_message,
            title=metadata['title'],
            author=metadata['author'],
            creation_date=datetime.strptime(
                metadata['creation_date'], "D:%Y%m%d%H%M%S") if metadata['creation_date'] else None,
            page_count=metadata['page_count'],
            word_count=metadata['word_count']
        )

        return document_message
