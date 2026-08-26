import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone

SIGNUP_OTP_TTL_MINUTES = 10
LOGIN_OTP_TTL_MINUTES = 5
MAX_OTP_ATTEMPTS = 5


class EmailOTP(models.Model):
    """
    A one-time code emailed to a user for either verifying a new account
    (purpose=signup) or completing a login as a second factor
    (purpose=login). Each row is single-use: once verified or expired, a
    fresh one is generated rather than reusing/extending it.
    """

    class Purpose(models.TextChoices):
        SIGNUP = "signup", "Signup verification"
        LOGIN = "login", "Login verification"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="otps",
    )

    purpose = models.CharField(max_length=10, choices=Purpose.choices)

    code = models.CharField(max_length=6)

    created_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField()

    is_used = models.BooleanField(default=False)

    attempts = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} — {self.purpose} — {'used' if self.is_used else 'active'}"

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @property
    def is_locked_out(self):
        return self.attempts >= MAX_OTP_ATTEMPTS

    @staticmethod
    def generate_code():
        """A 6-digit code, zero-padded, using a CSPRNG rather than random."""
        return f"{secrets.randbelow(1_000_000):06d}"

    @classmethod
    def issue(cls, user, purpose):
        """Invalidates any older unused codes for this user+purpose, then issues a fresh one."""

        cls.objects.filter(user=user, purpose=purpose, is_used=False).update(is_used=True)

        ttl = SIGNUP_OTP_TTL_MINUTES if purpose == cls.Purpose.SIGNUP else LOGIN_OTP_TTL_MINUTES

        return cls.objects.create(
            user=user,
            purpose=purpose,
            code=cls.generate_code(),
            expires_at=timezone.now() + timezone.timedelta(minutes=ttl),
        )
