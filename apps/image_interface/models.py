from django.db import models
from django.core.exceptions import ValidationError
from PIL import Image

IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')


def validate_image(image):
    if not image.name.lower().endswith(IMAGE_EXTENSIONS):
        raise ValidationError(
            "Unsupported file extension. Please upload a valid image file.")
    try:
        img = Image.open(image)
        img.verify()
    except:
        raise ValidationError(
            "Invalid image file. Please upload a valid image.")


class ImageMessage(models.Model):
    message = models.OneToOneField(
        'chat.Message',
        on_delete=models.CASCADE,
        related_name='image_content'
    )
    image = models.ImageField(
        upload_to='image_messages/',
        validators=[validate_image]
    )
    width = models.IntegerField()
    height = models.IntegerField()
    description = models.TextField()

    def __str__(self):
        return f"Image Message {self.id}"
