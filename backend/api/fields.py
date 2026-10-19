"""Custom serializer fields."""

import base64

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Image field that accepts images encoded as base64 data URLs.

    The frontend sends images as strings like
    ``data:image/png;base64,iVBORw0...``. Such strings are decoded into
    a file; any other value is handled by the regular ``ImageField``.
    """

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            metadata, image_code = data.split(';base64,')
            extension = metadata.split('/')[-1]
            data = ContentFile(
                base64.b64decode(image_code),
                name=f'temp.{extension}'
            )
        return super().to_internal_value(data)
