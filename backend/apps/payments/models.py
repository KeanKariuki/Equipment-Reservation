from django.db import models

from apps.reservations.models import Reservation


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    # One reservation gets one payment attempt-chain. If a payment fails,
    # we reuse this row with a fresh reference rather than creating a new
    # one, so there's always a single source of truth per reservation.
    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.CASCADE,
        related_name="payment",
    )

    reference = models.CharField(max_length=100, unique=True)

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="KES. Matches reservation.total_amount at the time of initialization.",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    paystack_transaction_id = models.CharField(max_length=100, blank=True)

    channel = models.CharField(
        max_length=50,
        blank=True,
        help_text="How they paid, e.g. card, mobile_money, bank_transfer.",
    )

    paid_at = models.DateTimeField(null=True, blank=True)

    raw_response = models.JSONField(
        null=True,
        blank=True,
        help_text="Last Paystack response for this payment, kept for support/debugging.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference} — {self.status}"
