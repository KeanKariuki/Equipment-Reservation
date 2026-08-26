from rest_framework import serializers

from apps.resources.models import Resource
from apps.resources.serializers import ResourceSerializer

from .models import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    """Read serializer — includes the nested resource for display."""

    resource = ResourceSerializer(read_only=True)
    payment_status = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = [
            "id",
            "resource",
            "start_datetime",
            "end_datetime",
            "status",
            "subtotal",
            "security_deposit",
            "total_amount",
            "payment_status",
            "created_at",
        ]
        read_only_fields = fields

    def get_payment_status(self, obj):
        payment = getattr(obj, "payment", None)
        return payment.status if payment else None


class ReservationCreateSerializer(serializers.Serializer):
    """Write serializer — the service layer computes pricing and status."""

    resource_id = serializers.PrimaryKeyRelatedField(
        queryset=Resource.objects.filter(is_active=True),
        source="resource",
    )
    start_datetime = serializers.DateTimeField()
    end_datetime = serializers.DateTimeField()
