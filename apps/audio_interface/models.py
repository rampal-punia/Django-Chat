from django.db import models


class AudioMessage(models.Model):
    message = models.OneToOneField(
        'chat.Message',
        on_delete=models.CASCADE,
        related_name='audio_content'
    )
    audio_file = models.FileField(upload_to='voice_messages/')
    transcript = models.TextField()
    duration = models.FloatField()  # in seconds
