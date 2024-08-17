import os

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from . import helper


class Musician(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    instrument = models.CharField(max_length=100)


class Album(models.Model):
    artist = models.ForeignKey(Musician, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    release_date = models.DateField()
    num_stars = models.IntegerField()


class ImageFile(models.Model):
    album = models.ForeignKey(Album,
                              on_delete=models.CASCADE,
                              related_name='images',
                              null=True,
                              )
    image = models.ImageField(upload_to="images")

    @property
    def get_imageurl(self):
        return self.image.path

    @property
    def get_filename(self):
        return os.path.split(self.image.path)[-1]

    def get_absolute_url(self):
        return reverse("artist:model_detail_url", kwargs={"pk": self.pk})
