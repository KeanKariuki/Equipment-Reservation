import math

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.reservations.models import Reservation


def price_reservation(resource, start_datetime, end_datetime):
    """
    Computes subtotal, deposit, and total for a resource + time window,
    based on the resource's pricing_unit (hourly or daily). The security
    deposit is half of the rental subtotal.
    Partial hours/days are rounded up to the next whole unit.
    """

    duration = end_datetime - start_datetime
    seconds = duration.total_seconds()

    if resource.pricing_unit == resource.PricingUnit.HOURLY:
        units = max(1, math.ceil(seconds / 3600))
    else:
        units = max(1, math.ceil(seconds / 86400))

    subtotal = resource.price * units
    deposit = subtotal / 2
    total = subtotal 

    return {
        "subtotal": subtotal,
        "security_deposit": deposit,
        "total_amount": total,
    }


def check_availability(resource, start_datetime, end_datetime):
    """
    Returns True if the resource has no conflicting active reservations.
    """

    conflicting_reservations = Reservation.objects.filter(
        resource=resource,
        start_datetime__lt=end_datetime,
        end_datetime__gt=start_datetime,
        status__in=[
            Reservation.Status.PENDING,
            Reservation.Status.CONFIRMED,
        ],
    )

    return not conflicting_reservations.exists()


@transaction.atomic
def create_reservation(
    *,
    resource,
    user,
    start_datetime,
    end_datetime,
):
    """
    Creates a reservation safely.

    PostgreSQL's exclusion constraint provides the final protection
    against simultaneous overlapping bookings.
    """

    if start_datetime >= end_datetime:
        raise ValueError(
            "End datetime must be after start datetime."
        )

    if start_datetime < timezone.now():
        raise ValueError(
            "Start datetime can't be in the past."
        )

    if not check_availability(
        resource,
        start_datetime,
        end_datetime,
    ):
        raise ValueError(
            "This resource is not available for the selected time."
        )

    pricing = price_reservation(resource, start_datetime, end_datetime)

    try:
        reservation = Reservation.objects.create(
            resource=resource,
            user=user,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            status=Reservation.Status.PENDING,
            **pricing,
        )

        return reservation

    except IntegrityError as error:
        raise ValueError(
            "This resource was just reserved for the selected time."
        ) from error