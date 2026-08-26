from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
        read_only_fields = ["id"]

    def validate_email(self, value):
        # Default Django's User.email isn't unique at the DB level, but we
        # rely on it as the OTP delivery address and (via username lookup)
        # for login, so it needs to behave as unique in practice. A
        # verified account with this email always blocks; an unverified
        # (still-pending) one doesn't -- see create() below.
        if User.objects.filter(email__iexact=value, is_active=True).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def create(self, validated_data):
        # Re-registering with the same username while the original signup
        # is still pending (unverified) reuses that row and just gets a
        # fresh OTP, rather than erroring on the username's uniqueness
        # constraint -- handles "I never got the email" gracefully.
        existing = User.objects.filter(
            username=validated_data["username"], is_active=False
        ).first()

        if existing:
            existing.email = validated_data["email"]
            existing.set_password(validated_data["password"])
            existing.save(update_fields=["email", "password"])
            return existing

        user = User.objects.create_user(**validated_data)
        user.is_active = False
        user.save(update_fields=["is_active"])
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class LoginSerializer(serializers.Serializer):
    """Validates credentials only. Does not issue a token -- that only
    happens after the OTP step, in VerifyLoginOTPView."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class OTPVerifySerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    code = serializers.RegexField(r"^\d{6}$")
