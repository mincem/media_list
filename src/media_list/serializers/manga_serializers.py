from rest_framework import serializers

from ..models import MangaSeries, MangaURL


class MangaURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = MangaURL
        fields = ["id", "url"]


class MangaSerializer(serializers.ModelSerializer):
    urls = MangaURLSerializer(many=True, allow_null=True, required=False)

    class Meta:
        model = MangaSeries
        fields = ["id", "title", "alternate_title", "volumes", "interest", "status", "is_completed", "urls"]

    def create(self, validated_data):
        urls_data = validated_data.pop("urls", [])
        manga = MangaSeries.objects.create(**validated_data)
        for url_data in urls_data:
            manga.urls.get_or_create(**url_data)
        return manga

    def update(self, instance, validated_data):
        urls_data = validated_data.pop("urls", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        for url_data in urls_data:
            instance.urls.get_or_create(**url_data)
        return instance
