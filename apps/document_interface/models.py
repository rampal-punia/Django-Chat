from django.db import models
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from pgvector.django import VectorField
import magic


def validate_pdf(document):
    if isinstance(document, UploadedFile):
        # Check the MIME type of the file
        mime = magic.Magic(mime=True)
        file_type = mime.from_buffer(document.read(1024))
        if file_type != 'application/pdf':
            raise ValidationError("The uploaded file is not a valid PDF.")
        # Reset the file pointer
        document.seek(0)
    else:
        raise ValidationError("Invalid file upload.")


class DocumentChunk(models.Model):
    document = models.ForeignKey(
        'DocumentMessage',
        on_delete=models.CASCADE,
        related_name='chunks'
    )
    content = models.TextField()
    embedding = VectorField(dimensions=384)
    metadata = models.JSONField(default=dict)

    def __str__(self):
        return f"Chunk {self.id} of Document {self.document.id}"


class DocumentMessage(models.Model):
    message = models.OneToOneField(
        'chat.Message',
        on_delete=models.CASCADE,
        related_name='document_content'
    )
    document = models.FileField(
        upload_to='document_messages/',
        validators=[validate_pdf]
    )
    num_pages = models.IntegerField()
    num_chunks = models.IntegerField()
    # Store the actual MIME type
    file_type = models.CharField(max_length=255)
    # Store the full processed text content
    processed_content = models.TextField(blank=True)
    # Store the generated summary
    summary = models.TextField(blank=True)
    # Field for storing the hash (Check same file uploaded again)
    document_hash = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"Document: {self.id}"

    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation
            mime = magic.Magic(mime=True)
            self.file_type = mime.from_buffer(self.document.read(1024))
            self.document.seek(0)  # Reset file pointer
        super().save(*args, **kwargs)


class DocumentMetadata(models.Model):
    document = models.OneToOneField(
        DocumentMessage, on_delete=models.CASCADE, related_name='metadata')
    title = models.CharField(max_length=255, blank=True)
    author = models.CharField(max_length=255, blank=True)
    last_modified_date = models.DateTimeField(null=True, blank=True)
    page_count = models.IntegerField(null=True)
    word_count = models.IntegerField(null=True)

    def __str__(self):
        return f"Metadata for Document {self.document.id}"
