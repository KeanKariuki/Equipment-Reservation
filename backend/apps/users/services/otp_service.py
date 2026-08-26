from django.core.mail import send_mail

from apps.users.models import EmailOTP

SUBJECTS = {
    EmailOTP.Purpose.SIGNUP: "Verify your Field Manual account",
    EmailOTP.Purpose.LOGIN: "Your Field Manual sign-in code",
}


def send_otp(user, purpose):
    """Issues a fresh OTP for user+purpose and emails it. Returns the OTP row."""

    otp = EmailOTP.issue(user, purpose)

    if purpose == EmailOTP.Purpose.SIGNUP:
        body = (
            f"Hi {user.username},\n\n"
            f"Your verification code is: {otp.code}\n\n"
            f"It expires in 10 minutes. Enter it to activate your account."
        )
    else:
        body = (
            f"Hi {user.username},\n\n"
            f"Your sign-in code is: {otp.code}\n\n"
            f"It expires in 5 minutes. If this wasn't you, you can ignore this email."
        )

    send_mail(
        subject=SUBJECTS[purpose],
        message=body,
        from_email=None,  # falls back to settings.DEFAULT_FROM_EMAIL
        recipient_list=[user.email],
    )

    return otp


def verify_otp(user, purpose, code):
    """
    Checks the most recent unused OTP for user+purpose against `code`.
    Raises ValueError with a user-facing message on any failure; consumes
    (marks used) the OTP on success so it can't be replayed.
    """

    otp = (
        EmailOTP.objects.filter(user=user, purpose=purpose, is_used=False)
        .order_by("-created_at")
        .first()
    )

    if not otp:
        raise ValueError("No verification code is pending. Request a new one.")

    if otp.is_expired:
        raise ValueError("That code has expired. Request a new one.")

    if otp.is_locked_out:
        raise ValueError("Too many incorrect attempts. Request a new code.")

    if otp.code != code:
        otp.attempts += 1
        otp.save(update_fields=["attempts"])
        raise ValueError("That code doesn't match.")

    otp.is_used = True
    otp.save(update_fields=["is_used"])

    return otp
