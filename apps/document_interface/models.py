from django.core.exceptions import ValidationError
from django.db import models
from pypdf import PdfReader
from pgvector.django import VectorField

DOCUMENT_EXTENSIONS = ('.pdf', )


def validate_document(document):
    if not document.name.lower().endswith(DOCUMENT_EXTENSIONS):
        raise ValidationError(
            "Unsupported file extension. Please upload a valid document file.")
    try:
        doc = PdfReader.read(document)
    except:
        raise ValidationError(
            "Invalid document file. Please upload a valid document.")


class DocumentMessage(models.Model):
    message = models.OneToOneField(
        'chat.Message',
        on_delete=models.CASCADE,
        related_name='document_content'
    )
    document = models.FileField(upload_to='document_messages/')
    num_pages = models.IntegerField()
    file_type = models.CharField(max_length=10)  # e.g., 'pdf', 'docx'

    def __str__(self):
        return f"Document: {self.id}"
