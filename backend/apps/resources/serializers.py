from rest_framework import serializers

from .models import Resource


class ResourceSerializer(serializers.ModelSerializer):
    # The frontend only cares about one photo URL. An uploaded image (via
    # admin) takes priority; a linked image_url is used as a fallback.
    # Built as an absolute URL so it works directly in an <img src>.
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = [
            "id",
            "name",
            "description",
            "resource_type",
            "category",
            "price",
            "pricing_unit",
            "image_url",
            "security_deposit",
            "location",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_image_url(self, obj):
        url = obj.photo_url
        if not url:
            return None

        request = self.context.get("request")
        if request and url.startswith("/"):
            return request.build_absolute_uri(url)
        return url
