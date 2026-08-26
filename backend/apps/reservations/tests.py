from datetime import datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

from django.test import SimpleTestCase

from apps.reservations.services.reservation_service import price_reservation


class ReservationPricingTests(SimpleTestCase):
	def test_security_deposit_is_half_of_rental_subtotal(self):
		resource = SimpleNamespace(
			price=Decimal("1200.00"),
			pricing_unit="hour",
			PricingUnit=SimpleNamespace(HOURLY="hour"),
		)
		start = datetime(2026, 9, 1, 10, 0)
		end = start + timedelta(hours=3)

		pricing = price_reservation(resource, start, end)

		self.assertEqual(pricing["subtotal"], Decimal("3600.00"))
		self.assertEqual(pricing["security_deposit"], Decimal("1800.00"))
		self.assertEqual(pricing["total_amount"], Decimal("5400.00"))
