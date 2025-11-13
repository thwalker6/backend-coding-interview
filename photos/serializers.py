from rest_framework import serializers
from .models import Photo, Photographer


class PhotoOfPhotographersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = [
            "id",
            "photo_id",
            "src_url",
            "alt",
        ]


class PhotographerSerializer(serializers.ModelSerializer):
    photo_count = serializers.ReadOnlyField()
    photos = PhotoOfPhotographersSerializer(many=True, read_only=True)

    class Meta:
        model = Photographer
        fields = ["id", "photographer_id", "name", "url", "photo_count", "photos"]


class PhotographerListSerializer(serializers.ModelSerializer):
    photo_count = serializers.ReadOnlyField()

    class Meta:
        model = Photographer
        fields = ["id", "name", "photographer_id", "url", "photo_count"]


class PhotoSerializer(serializers.ModelSerializer):
    portrait_url = serializers.ReadOnlyField()
    landscape_url = serializers.ReadOnlyField()
    tiny_pic_url = serializers.ReadOnlyField()
    extra_large_pic_url = serializers.ReadOnlyField()
    large_pic_url = serializers.ReadOnlyField()
    small_pic_url = serializers.ReadOnlyField()
    medium_pic_url = serializers.ReadOnlyField()

    photographer = PhotographerListSerializer(read_only=True)

    class Meta:
        model = Photo
        fields = [
            "id",
            "photo_id",
            "width",
            "height",
            "url",
            "src_url",
            "photographer",
            "avg_color",
            "alt",
            "portrait_url",
            "landscape_url",
            "extra_large_pic_url",
            "large_pic_url",
            "small_pic_url",
            "medium_pic_url",
            "tiny_pic_url",
            "created_at",
            "updated_at",
        ]


class PhotoListSerializer(serializers.ModelSerializer):
    photographer_name = serializers.CharField(
        source="photographer.name", read_only=True
    )

    class Meta:
        model = Photo
        fields = [
            "id",
            "photo_id",
            "width",
            "url",
            "src_url",
            "height",
            "photographer_name",
            "avg_color",
            "alt",
        ]


class PhotoCreateSerializer(serializers.ModelSerializer):
    photographer = PhotographerSerializer(required=True)

    class Meta:
        model = Photo
        fields = [
            "photo_id",
            "width",
            "height",
            "url",
            "photographer",
            "avg_color",
            "alt",
            "src_url",
        ]

    def create(self, validated_data):
        photographer_data = validated_data.pop("photographer", None)
        photographer = None

        if photographer_data:
            lookup_fields = {
                "name": photographer_data.pop("name"),
                "photographer_id": photographer_data.pop("photographer_id"),
            }

            photographer, created = Photographer.objects.get_or_create(
                **lookup_fields, defaults=photographer_data
            )

        photo = Photo.objects.create(photographer=photographer, **validated_data)
        return photo
