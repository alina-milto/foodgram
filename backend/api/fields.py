import base64

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            metadata, image_code = data.split(';base64,')
            extension = metadata.split('/')[-1]
            data = ContentFile(
                base64.b64decode(image_code),
                name=f'temp.{extension}'
            )
        return super().to_internal_value(data)
