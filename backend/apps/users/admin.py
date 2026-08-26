from django.contrib import admin

from .models import EmailOTP


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    """Read-only, for debugging delivery/verification issues -- not for
    manually issuing or approving codes."""

    list_display = ("user", "purpose", "code", "is_used", "attempts", "created_at", "expires_at")
    list_filter = ("purpose", "is_used")
    search_fields = ("user__username", "user__email")
    readonly_fields = [f.name for f in EmailOTP._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
