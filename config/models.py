from urllib.parse import urlparse, urlunparse
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import FieldError


class CreationModificationDateBase(models.Model):
    """
    Abstract base class with a creation and modification date and time
    """

    created = models.DateTimeField(
        _("Creation Date and Time"),
        auto_now_add=True,
    )

    modified = models.DateTimeField(
        _("Modification Date and Time"),
        auto_now=True,
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        print("save() from CreationModificationDateBase called")
    save.alters_data = True

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        print("delete() from CreationModificationDateBase called")

    def test(self):
        print("test() from CreationModificationDateBase called")
