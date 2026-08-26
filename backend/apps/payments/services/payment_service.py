from django.db import transaction
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from apps.reservations.models import Reservation

from ..models import Payment
from .paystack_service import from_kobo, generate_reference


def start_payment(reservation):
    """
    Gets (or creates) the Payment row for a reservation. Reused across
    retries -- a previous failed attempt gets a fresh reference rather than
    piling up duplicate Payment rows for the same booking.
    """

    payment, created = Payment.objects.get_or_create(
        reservation=reservation,
        defaults={
            "reference": generate_reference(),
            "amount": reservation.total_amount,
        },
    )

    if not created and payment.status == Payment.Status.FAILED:
        payment.reference = generate_reference()
        payment.status = Payment.Status.PENDING
        payment.save(update_fields=["reference", "status", "updated_at"])

    return payment


@transaction.atomic
def apply_paystack_result(payment, data):
    """
    Applies a Paystack transaction payload (from either the verify endpoint
    or the webhook) to a Payment, and confirms the reservation on success.

    Idempotent by design: whichever of "the frontend calls verify" or "the
    webhook arrives" gets there first wins, and the other becomes a no-op.
    Locks the row so the verify-call and the webhook can't race each other.
    """

    payment = (
        Payment.objects.select_for_update()
        .select_related("reservation")
        .get(pk=payment.pk)
    )

    if payment.status == Payment.Status.SUCCESS:
        return payment

    if not data:
        return payment

    paystack_status = data.get("status")
    amount_paid = from_kobo(data.get("amount", 0))

    payment.raw_response = data

    if paystack_status == "success" and amount_paid >= float(payment.amount):
        payment.status = Payment.Status.SUCCESS
        payment.paystack_transaction_id = str(data.get("id", ""))
        payment.channel = data.get("channel", "")
        payment.paid_at = parse_datetime(data.get("paid_at") or "") or timezone.now()
        payment.save()

        reservation = payment.reservation
        reservation.status = Reservation.Status.CONFIRMED
        reservation.save(update_fields=["status", "updated_at"])
    else:
        payment.status = Payment.Status.FAILED
        payment.save()

    return payment
