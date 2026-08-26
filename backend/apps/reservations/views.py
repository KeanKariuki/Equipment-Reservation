from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Reservation
from .serializers import ReservationCreateSerializer, ReservationSerializer
from .services.reservation_service import create_reservation


class ReservationViewSet(viewsets.ModelViewSet):
    """
    A user's own reservations. Create checks availability and computes
    pricing server-side via the reservation service.
    """

    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        return (
            Reservation.objects.filter(user=self.request.user)
            .select_related("resource", "payment")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return ReservationCreateSerializer
        return ReservationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            reservation = create_reservation(
                resource=serializer.validated_data["resource"],
                user=request.user,
                start_datetime=serializer.validated_data["start_datetime"],
                end_datetime=serializer.validated_data["end_datetime"],
            )
        except ValueError as error:
            return Response({"detail": str(error)}, status=status.HTTP_400_BAD_REQUEST)

        output = ReservationSerializer(reservation)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """Cancelling a reservation sets status rather than deleting it."""

        reservation = self.get_object()
        reservation.status = Reservation.Status.CANCELLED
        reservation.save(update_fields=["status", "updated_at"])
        return Response(ReservationSerializer(reservation).data)

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        queryset = self.get_queryset().filter(
            status__in=[Reservation.Status.PENDING, Reservation.Status.CONFIRMED],
        )
        serializer = ReservationSerializer(queryset, many=True)
        return Response(serializer.data)
