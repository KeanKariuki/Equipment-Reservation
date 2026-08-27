import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Creates (or updates the password of) a superuser from environment
    variables. Safe to run on every deploy -- unlike `createsuperuser
    --noinput`, it won't fail the build if the account already exists.

    Intended for hosts with no shell access on the free tier (e.g. Render):
    add this as the last step of the build command instead of running
    `createsuperuser` interactively.

    Requires DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, and
    DJANGO_SUPERUSER_PASSWORD to be set. If any are missing, it does
    nothing (so local dev builds without these vars aren't affected).
    """

    help = "Create or update the admin superuser from environment variables."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not username or not password:
            self.stdout.write(
                "DJANGO_SUPERUSER_USERNAME / DJANGO_SUPERUSER_PASSWORD not "
                "set -- skipping superuser setup."
            )
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "is_staff": True, "is_superuser": True},
        )

        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}'."))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Superuser '{username}' already existed -- password updated.")
            )
