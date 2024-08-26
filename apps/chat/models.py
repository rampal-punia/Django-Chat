import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from config.models import CreationModificationDateBase
from django.contrib.auth import get_user_model


User = get_user_model()


class Conversation(CreationModificationDateBase):
    class Status(models.TextChoices):
        ACTIVE = 'AC', _('Active')
        ARCHIVED = 'AR', _('Archived')
        ENDED = 'EN', _('Ended')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(
        max_length=255,
        default='Untitled Conversation'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversations',
    )
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['user', 'created']),
            models.Index(fields=['status'])
        ]

    def __str__(self) -> str:
        return f"{self.user.username} - {self.title[:40]}..."


class Message(CreationModificationDateBase):
    class ContentType(models.TextChoices):
        TEXT = 'TE', _('Text')
        IMAGE = 'IM', _('Image')
        AUDIO = 'AU', _('Audio')
        VIDEO = 'VI', _('Video')
        DOCUMENT = 'DO', _('Document')

    conversation = models.ForeignKey(
        'chat.Conversation',
        on_delete=models.CASCADE,
        related_name='messages'
    )
    content_type = models.CharField(
        max_length=2,
        choices=ContentType.choices,
        default=ContentType.TEXT
    )
    is_from_user = models.BooleanField(default=True)
    in_reply_to = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='replies'
    )

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['conversation', 'created']),
            models.Index(fields=['is_from_user'])
        ]


class ChatMessage(models.Model):
    message = models.OneToOneField(
        'chat.Message',
        on_delete=models.CASCADE,
        related_name="chat_content"
    )
    content = models.TextField(default='No Text Data Found')

    def __str__(self) -> str:
        return f"{self.id} - {self.content[:50]}"
