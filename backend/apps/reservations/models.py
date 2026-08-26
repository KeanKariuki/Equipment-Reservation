from django.conf import settings
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import RangeOperators
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from apps.resources.models import Resource


class Reservation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    resource = models.ForeignKey(
        Resource,
        on_delete=models.PROTECT,
        related_name="reservations",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reservations",
    )

    start_datetime = models.DateTimeField()

    end_datetime = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    security_deposit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()

        if self.start_datetime and self.end_datetime:
            if self.start_datetime >= self.end_datetime:
                raise ValidationError(
                    "End datetime must be after start datetime."
                )

        # Only enforce "not in the past" when the reservation is first
        # created. Editing an existing (now-past) reservation later -- e.g.
        # marking it completed -- shouldn't be blocked by this.
        if self.pk is None and self.start_datetime:
            if self.start_datetime < timezone.now():
                raise ValidationError(
                    "Start datetime can't be in the past."
                )

    class Meta:
        ordering = ["-start_datetime"]

        constraints = [
            models.CheckConstraint(
                condition=Q(start_datetime__lt=F("end_datetime")),
                name="reservation_start_before_end",
            ),
            ExclusionConstraint(
                name="prevent_overlapping_active_reservations",
                expressions=[
                    (
                        "resource",
                        RangeOperators.EQUAL,
                    ),
                    (
                        models.Func(
                            F("start_datetime"),
                            F("end_datetime"),
                            function="TSTZRANGE",
                        ),
                        RangeOperators.OVERLAPS,
                    ),
                ],
                condition=Q(
                    status__in=[
                        "pending",
                        "confirmed",
                    ]
                ),
            ),
        ]

    def __str__(self):
        return (
            f"{self.resource.name} - "
            f"{self.start_datetime:%Y-%m-%d %H:%M}"
        )
