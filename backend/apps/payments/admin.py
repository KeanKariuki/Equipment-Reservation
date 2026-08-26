from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Read-mostly: payment status should only ever change via Paystack's
    verify response or webhook (see services/payment_service.py), never by
    someone hand-editing it here and creating a mismatch with what
    actually happened on Paystack's side.
    """

    list_display = (
        "reference",
        "reservation",
        "amount",
        "status",
        "channel",
        "paid_at",
    )

    list_filter = ("status", "channel")

    search_fields = ("reference", "paystack_transaction_id", "reservation__id")

    readonly_fields = (
        "reservation",
        "reference",
        "amount",
        "status",
        "paystack_transaction_id",
        "channel",
        "paid_at",
        "raw_response",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    class Media:
        css = {"all": ("admin/css/field_manual_admin.css",)}
