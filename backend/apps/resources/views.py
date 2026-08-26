from django.utils.dateparse import parse_datetime
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.reservations.services.reservation_service import check_availability

from .models import Resource
from .serializers import ResourceSerializer


class ResourceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Browse available equipment and spaces.

    Supports filtering with ?resource_type=equipment|space and
    ?category=<category>.
    """

    serializer_class = ResourceSerializer

    def get_queryset(self):
        queryset = Resource.objects.filter(is_active=True)

        resource_type = self.request.query_params.get("resource_type")
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)

        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category__iexact=category)

        return queryset

    @action(detail=True, methods=["get"])
    def availability(self, request, pk=None):
        """
        ?start=<ISO datetime>&end=<ISO datetime>
        Returns whether this resource is free for the given window.
        """

        resource = self.get_object()

        start = parse_datetime(request.query_params.get("start", ""))
        end = parse_datetime(request.query_params.get("end", ""))

        if not start or not end:
            return Response(
                {"detail": "Provide start and end as ISO 8601 datetimes."},
                status=400,
            )

        is_available = check_availability(resource, start, end)
        return Response({"available": is_available})
