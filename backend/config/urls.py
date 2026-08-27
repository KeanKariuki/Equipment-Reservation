"""
URL configuration for config project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.static import serve as serve_static_file
from rest_framework.routers import DefaultRouter

from apps.payments.views import InitializePaymentView, VerifyPaymentView, paystack_webhook
from apps.reservations.views import ReservationViewSet
from apps.resources.views import ResourceViewSet
from apps.users.views import (
    LoginRequestView,
    MeView,
    RegisterView,
    ResendOTPView,
    VerifyLoginOTPView,
    VerifyRegisterOTPView,
)

admin.site.site_header = "Field Manual — Admin"
admin.site.site_title = "Field Manual Admin"
admin.site.index_title = "Depot management"

router = DefaultRouter()
router.register("resources", ResourceViewSet, basename="resource")
router.register("reservations", ReservationViewSet, basename="reservation")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/register/verify/", VerifyRegisterOTPView.as_view(), name="register-verify"),
    path("api/auth/login/", LoginRequestView.as_view(), name="login"),
    path("api/auth/login/verify/", VerifyLoginOTPView.as_view(), name="login-verify"),
    path("api/auth/otp/resend/", ResendOTPView.as_view(), name="otp-resend"),
    path("api/auth/me/", MeView.as_view(), name="me"),
    path("api/payments/initialize/", InitializePaymentView.as_view(), name="payment-initialize"),
    path("api/payments/verify/", VerifyPaymentView.as_view(), name="payment-verify"),
    path("api/payments/webhook/", paystack_webhook, name="payment-webhook"),
    # Demo/seed photos committed to the repo (backend/seed_images/) -- unlike
    # uploaded media, these live in git, so they survive every deploy and
    # every restart, on any host, free tier or not.
    path(
        "seed-images/<path:path>",
        serve_static_file,
        {"document_root": settings.BASE_DIR / "seed_images"},
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
