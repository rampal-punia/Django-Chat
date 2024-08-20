from django.db import models


class ImageMessage(models.Model):
    message = models.OneToOneField(
        'chat.Message',
        on_delete=models.CASCADE,
        related_name='image_content'
    )
    image = models.ImageField(upload_to='image_messages/')
    width = models.IntegerField()
    height = models.IntegerField()
    description = models.TextField()
