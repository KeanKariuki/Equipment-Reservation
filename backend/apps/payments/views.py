import json
import logging

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.reservations.models import Reservation

from .models import Payment
from .serializers import PaymentSerializer
from .services.paystack_service import verify_transaction, verify_webhook_signature
from .services.payment_service import apply_paystack_result, start_payment

logger = logging.getLogger(__name__)


class InitializePaymentView(APIView):
    """
    POST /api/payments/initialize/  {"reservation_id": 12}

    Creates (or reuses) a Payment for one of the caller's own pending
    reservations and returns what the frontend needs to open the Paystack
    Inline popup. No money moves here -- Paystack's own popup collects
    card/mobile-money details directly, so this API never touches them.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        reservation_id = request.data.get("reservation_id")

        reservation = Reservation.objects.filter(
            id=reservation_id, user=request.user
        ).first()

        if not reservation:
            return Response({"detail": "Reservation not found."}, status=404)

        if reservation.status != Reservation.Status.PENDING:
            return Response(
                {"detail": "Only pending reservations can be paid for."},
                status=400,
            )

        if not settings.PAYSTACK_PUBLIC_KEY:
            return Response(
                {"detail": "Payments aren't configured yet. Set PAYSTACK_PUBLIC_KEY / PAYSTACK_SECRET_KEY."},
                status=503,
            )

        payment = start_payment(reservation)

        return Response({
            "public_key": settings.PAYSTACK_PUBLIC_KEY,
            "reference": payment.reference,
            "amount_kobo": int(round(payment.amount * 100)),
            "amount": payment.amount,
            "email": request.user.email,
        })


class VerifyPaymentView(APIView):
    """
    POST /api/payments/verify/  {"reference": "fm_..."}

    Called by the frontend right after the Paystack popup closes, purely so
    the UI can update immediately. This calls Paystack's own verify
    endpoint server-side (authenticated with the secret key) rather than
    trusting whatever the popup's callback says -- the webhook below is
    still what's authoritative if this call never happens.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        reference = request.data.get("reference")

        payment = (
            Payment.objects.filter(reference=reference, reservation__user=request.user)
            .select_related("reservation")
            .first()
        )

        if not payment:
            return Response({"detail": "Payment not found."}, status=404)

        try:
            data = verify_transaction(reference)
        except Exception:
            logger.exception("Paystack verify call failed for reference %s", reference)
            return Response(
                {"detail": "Could not reach Paystack to verify this payment. It will be confirmed automatically once the webhook arrives, if it succeeded."},
                status=502,
            )

        payment = apply_paystack_result(payment, data)

        return Response({
            "payment": PaymentSerializer(payment).data,
            "reservation_status": payment.reservation.status,
        })


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def paystack_webhook(request):
    """
    POST /api/payments/webhook/

    Paystack's server-to-server notification -- this is the source of
    truth for payment status, independent of whether the customer's
    browser ever calls VerifyPaymentView. Must stay open to unauthenticated
    requests (Paystack calls it directly), so the HMAC signature check is
    what keeps it safe: anything without a valid `x-paystack-signature` is
    rejected outright.
    """

    signature = request.headers.get("x-paystack-signature")

    if not verify_webhook_signature(request.body, signature):
        logger.warning("Rejected Paystack webhook with invalid signature.")
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    event = json.loads(request.body)

    if event.get("event") == "charge.success":
        data = event.get("data", {})
        reference = data.get("reference")

        payment = Payment.objects.filter(reference=reference).select_related("reservation").first()
        if payment:
            apply_paystack_result(payment, data)
        else:
            logger.warning("Paystack webhook for unknown reference %s", reference)

    # Always 200 so Paystack doesn't keep retrying events we've already
    # handled (or intentionally ignored, e.g. charge.failed).
    return Response(status=status.HTTP_200_OK)
