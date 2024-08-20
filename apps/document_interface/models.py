from django.db import models


class DocumentMessage(models.Model):
    message = models.OneToOneField(
        'chat.Message',
        on_delete=models.CASCADE,
        related_name='document_content'
    )
    document = models.FileField(upload_to='document_messages/')
    num_pages = models.IntegerField()
    file_type = models.CharField(max_length=10)  # e.g., 'pdf', 'docx'
