from rest_framework import serializers

from ..models import MangaSeries, MangaURL


class MangaURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = MangaURL
        fields = ["id", "url"]


class UrlsToDeleteSerializer(serializers.ListField):
    child = serializers.IntegerField()

    def get_attribute(self, instance):
        pass


class MangaSerializer(serializers.ModelSerializer):
    urls = MangaURLSerializer(many=True, allow_null=True, required=False)
    urls_to_delete = UrlsToDeleteSerializer()

    class Meta:
        model = MangaSeries
        fields = [
            "id", "title", "alternate_title", "volumes", "interest", "status", "is_completed", "urls", "urls_to_delete"
        ]

    def create(self, validated_data):
        validated_data.pop("urls_to_delete", [])
        urls_data = validated_data.pop("urls", [])
        manga = MangaSeries.objects.create(**validated_data)
        for url_data in urls_data:
            manga.urls.get_or_create(**url_data)
        return manga

    def update(self, instance, validated_data):
        urls_data = validated_data.pop("urls", [])
        urls_to_delete = validated_data.pop("urls_to_delete", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        for url_data in urls_data:
            instance.urls.get_or_create(**url_data)
        self.delete_urls(instance, urls_to_delete)
        return instance

    def delete_urls(self, manga, url_ids):
        urls = manga.urls
        urls_filter = urls.filter(pk__in=url_ids)
        urls_filter.delete()
