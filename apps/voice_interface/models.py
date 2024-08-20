from django.db import models


class VoiceMessage(models.Model):
    message = models.OneToOneField(
        'chat.Message',
        on_delete=models.CASCADE,
        related_name='voice_content'
    )
    audio_file = models.FileField(upload_to='voice_messages/')
    transcript = models.TextField()
    duration = models.FloatField()  # in seconds
