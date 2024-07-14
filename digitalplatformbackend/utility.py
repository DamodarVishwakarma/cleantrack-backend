from __future__ import absolute_import
import os
import sys
from io import BytesIO
from django.core.files import File
from PIL import Image

from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.deconstruct import deconstructible
_DEFAULT_TIMEOUT = 100
def compress_image(uploaded_image):
    image_temporary = Image.open(uploaded_image)
    output_io_stream = BytesIO()
    image_temporary.resize((1020, 573))
    image_temporary.save(output_io_stream, format='PNG', quality=60)
    output_io_stream.seek(0)
    return InMemoryUploadedFile(output_io_stream, 'ImageField', "%s.jpg" % uploaded_image.name.split('.')[0],
                                'image/jpeg', sys.getsizeof(output_io_stream), None)
from django.conf import settings
@deconstructible
class CustomImageStorage(Storage):
    """DropBox Storage class for Django pluggable storage sthumbnail_location = settings.MEDIA_ROOTystem."""
    thumbnail_location = settings.MEDIA_ROOT+'/Thumbnails'
    CHUNK_SIZE = 4 * 1024 * 1024
    def __init__(self):
        try:
            if not os.path.exists(self.thumbnail_location):
                os.makedirs(self.thumbnail_location)
        except FileExistsError:
            pass
    def _full_path(self, name):
        return '' if name == '/' else name
    def delete(self, name):
        try:
            os.remove(name)
        except Exception as e:
            print(e)
        try:
            os.remove(self.thumbnail_location + '/' + name)
        except FileNotFoundError:
            pass
    def exists(self, name):
        return os.path.exists(name)
    def url(self, name):
        return f'{settings.MEDIA_URL}{name}'
    def _open(self, name, mode='rb'):
        return open(name, mode)
    def _save(self, name, content):
        compressed_image = compress_image(content)
        try:
            with open(self.thumbnail_location + '/' + name, 'wb') as f:
                f.write(content.read())
                f.write(compressed_image.read())
        except FileNotFoundError:
            os.makedirs('/'.join((self.thumbnail_location + '/' + name).split('/')[0:-1]))
            with open(self.thumbnail_location + '/' + name, 'wb') as f:
                f.write(compressed_image.read())
        return name