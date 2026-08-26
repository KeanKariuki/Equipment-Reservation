from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EmailOTP
from .serializers import (
    LoginSerializer,
    OTPVerifySerializer,
    RegisterSerializer,
    UserSerializer,
)
from .services.otp_service import send_otp, verify_otp

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/  {username, email, password}

    Creates the account inactive and emails a signup OTP. No token yet --
    the account only becomes usable once /register/verify/ succeeds.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        send_otp(user, EmailOTP.Purpose.SIGNUP)

        return Response(
            {
                "detail": "Check your email for a verification code.",
                "user_id": user.id,
                "email": user.email,
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyRegisterOTPView(APIView):
    """
    POST /api/auth/register/verify/  {user_id, code}

    Activates the account and returns a token on success.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(
            id=serializer.validated_data["user_id"], is_active=False
        ).first()
        if not user:
            return Response({"detail": "Account not found or already verified."}, status=404)

        try:
            verify_otp(user, EmailOTP.Purpose.SIGNUP, serializer.validated_data["code"])
        except ValueError as error:
            return Response({"detail": str(error)}, status=400)

        user.is_active = True
        user.save(update_fields=["is_active"])

        token, _ = Token.objects.get_or_create(user=user)
        return Response({"user": UserSerializer(user).data, "token": token.key})


class LoginRequestView(APIView):
    """
    POST /api/auth/login/  {username, password}

    Checks credentials. On success, emails a login OTP instead of
    returning a token directly -- the token only comes back from
    /login/verify/. This is what makes it real 2FA rather than just
    password auth with an extra step the client could skip.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(
            username=serializer.validated_data["username"]
        ).first()

        # Deliberately the same generic message whether the username
        # doesn't exist or the password is wrong -- distinguishing the two
        # would let an attacker enumerate valid usernames. Checking the
        # password directly (rather than via authenticate()) is what lets
        # us still tell "wrong password" apart from "correct password,
        # account just isn't verified yet" below -- authenticate() folds
        # both into a plain None for an inactive user.
        if not user or not user.check_password(serializer.validated_data["password"]):
            return Response({"detail": "Incorrect username or password."}, status=400)

        if not user.is_active:
            send_otp(user, EmailOTP.Purpose.SIGNUP)
            return Response(
                {
                    "detail": "This account hasn't been verified yet. A new verification code has been sent.",
                    "user_id": user.id,
                    "requires": "signup_verification",
                },
                status=403,
            )

        send_otp(user, EmailOTP.Purpose.LOGIN)

        return Response(
            {
                "detail": "Enter the code sent to your email to finish signing in.",
                "user_id": user.id,
                "email": user.email,
            }
        )


class VerifyLoginOTPView(APIView):
    """
    POST /api/auth/login/verify/  {user_id, code}

    Second factor. Returns the token only after this succeeds.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(
            id=serializer.validated_data["user_id"], is_active=True
        ).first()
        if not user:
            return Response({"detail": "Account not found."}, status=404)

        try:
            verify_otp(user, EmailOTP.Purpose.LOGIN, serializer.validated_data["code"])
        except ValueError as error:
            return Response({"detail": str(error)}, status=400)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({"user": UserSerializer(user).data, "token": token.key})


class ResendOTPView(APIView):
    """
    POST /api/auth/otp/resend/  {user_id, purpose: "signup" | "login"}

    Lets the frontend offer a "didn't get a code?" button without making
    the person restart registration or login from scratch.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user_id = request.data.get("user_id")
        purpose = request.data.get("purpose")

        if purpose not in EmailOTP.Purpose.values:
            return Response({"detail": "Invalid purpose."}, status=400)

        is_active_required = purpose == EmailOTP.Purpose.LOGIN
        user = User.objects.filter(id=user_id, is_active=is_active_required).first()
        if not user:
            return Response({"detail": "Account not found."}, status=404)

        send_otp(user, purpose)
        return Response({"detail": "A new code has been sent."})


class MeView(APIView):
    """Returns the currently authenticated user."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
