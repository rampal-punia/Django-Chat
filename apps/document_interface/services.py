from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
import asyncio
import requests
import io
import base64

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

from django.conf import settings


API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_TOKEN}"}


class DocumentModalHandler:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vector_store = PGVector(
            collection_name="document_chunks",
            connection_string=settings.POSTGRES_CONNECTION_STRING,
            embedding_function=self.embeddings
        )

    async def process_document(self, document_content):
        # Save the document content to a temporary file
        temp_file = io.BytesIO(base64.b64decode(document_content))

        # Load the PDF
        loader = PyPDFLoader(temp_file)
        pages = loader.load()

        # Split the document into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_documents(pages)

        # Store chunks in the vector database
        await asyncio.to_thread(self.vector_store.add_documents, chunks)

        # Generate summary
        full_text = " ".join([chunk.page_content for chunk in chunks])
        # Limit to 4000 characters for API
        summary = await self.generate_summary_using_LLM(full_text[:4000])

        return len(chunks), summary

    async def generate_summary_using_LLM(self, text):
        response = await asyncio.to_thread(
            requests.post,
            API_URL,
            headers=headers,
            json={"inputs": text, "parameters": {
                "max_length": 300, "min_length": 100}}
        )
        return response.json()[0]['summary_text']

    async def query_document(self, query):
        results = await asyncio.to_thread(self.vector_store.similarity_search, query, k=3)
        context = " ".join([doc.page_content for doc in results])
        return context

    @staticmethod
    def update_document_message(document_message, num_chunks, summary):
        document_message.num_pages = num_chunks
        document_message.file_type = 'pdf'
        document_message.description = summary
        document_message.save()
