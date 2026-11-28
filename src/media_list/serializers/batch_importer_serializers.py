from rest_framework import serializers


class BatchLinkSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """A link sent to the batch importer: the bookmark's title as it came, and its URL."""
    text = serializers.CharField(allow_blank=True, trim_whitespace=False, max_length=1000)
    url = serializers.URLField(max_length=2000)


class BatchImporterInputSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    links = BatchLinkSerializer(many=True, allow_empty=False)
