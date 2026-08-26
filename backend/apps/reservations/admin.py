from django.contrib import admin

from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """
    Staff can create/edit reservations here too, not just through the API --
    so the same rules have to hold: no start time in the past (see
    Reservation.clean()), no overlapping bookings (DB exclusion
    constraint), and pricing fields stay accurate to what was actually
    charged rather than being freely editable after the fact.
    """

    list_display = (
        "id",
        "resource",
        "user",
        "start_datetime",
        "end_datetime",
        "status",
        "total_amount",
    )

    list_filter = ("status", "resource__resource_type")

    search_fields = (
        "resource__name",
        "user__username",
        "user__email",
    )

    autocomplete_fields = ("resource", "user")

    date_hierarchy = "start_datetime"

    ordering = ("-start_datetime",)

    readonly_fields = (
        "subtotal",
        "security_deposit",
        "total_amount",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("Booking", {
            "fields": ("resource", "user", "start_datetime", "end_datetime", "status"),
        }),
        ("Pricing (calculated, read-only)", {
            "fields": ("subtotal", "security_deposit", "total_amount"),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )

    class Media:
        css = {"all": ("admin/css/field_manual_admin.css",)}
