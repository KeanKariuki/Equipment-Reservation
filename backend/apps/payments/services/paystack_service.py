"""
Thin wrapper around Paystack's API. Two things matter most here:

1. We only ever trust Paystack's own servers about whether money actually
   moved -- never the browser. `verify_transaction` calls Paystack directly
   with the secret key. The webhook signature check does the same thing
   for server-to-server notifications.
2. Amounts to/from Paystack are in the smallest currency unit (cents for
   KES), so every amount crossing that boundary goes through to_kobo/
   from_kobo.
"""

import hashlib
import hmac
import uuid

import requests
from django.conf import settings

PAYSTACK_BASE_URL = "https://api.paystack.co"


def generate_reference():
    """A reference unique enough to never collide, readable enough to search for."""
    return f"fm_{uuid.uuid4().hex[:24]}"


def to_kobo(amount):
    return int(round(amount * 100))


def from_kobo(amount_kobo):
    return amount_kobo / 100


def verify_transaction(reference):
    """
    Calls GET /transaction/verify/:reference. Returns the transaction data
    dict on success, or None if Paystack doesn't recognize the reference.
    Raises requests.HTTPError on network/auth failures so callers don't
    silently treat a broken integration as "payment failed".
    """

    response = requests.get(
        f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}",
        headers={"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"},
        timeout=15,
    )
    response.raise_for_status()
    body = response.json()

    if not body.get("status"):
        return None

    return body["data"]


def verify_webhook_signature(request_body, signature_header):
    """
    Paystack signs every webhook payload with HMAC-SHA512 using your secret
    key, sent as the `x-paystack-signature` header. Recomputing and
    comparing it is what stops anyone from posting a fake "payment
    succeeded" event straight at the webhook endpoint.
    """

    if not signature_header or not settings.PAYSTACK_SECRET_KEY:
        return False

    computed = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode("utf-8"),
        request_body,
        hashlib.sha512,
    ).hexdigest()

    return hmac.compare_digest(computed, signature_header)
