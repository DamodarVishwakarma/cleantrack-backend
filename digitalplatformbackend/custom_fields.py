from django.conf import settings
from django.core.files.images import ImageFile
from django.db import models
from django.db.models.fields.files import FieldFile


class CustomImageAttributes(ImageFile, FieldFile):

    @property
    def thumbnail(self):
        return '/' + settings.THUMBNAIL_URL_PREFIX + '/' + self.name


class CustomImageField(models.ImageField):
    attr_class = CustomImageAttributes
