from django.core.management.base import BaseCommand

from apps.resources.models import Resource

# NOTE: image_url points to picsum.photos, a free placeholder-image service,
# and is only used as a fallback for items that don't have a real photo
# uploaded yet. Each seed below is a stable string, so the same item always
# gets the same placeholder (deterministic, no dead links). Once real photos
# are uploaded in the admin (the "image" field), the upload takes priority
# automatically -- no code changes needed.
EQUIPMENT = [
    {
        "name": "Full-Frame Mirrorless Body",
        "description": "45MP full-frame mirrorless camera body with in-body stabilization and dual card slots.",
        "category": "Camera Bodies",
        "price": 4500,
        "pricing_unit": Resource.PricingUnit.DAILY,
        "security_deposit": 30000,
        "location": "Nairobi Yard",
        "image_seed": "mirrorless-body-fullframe",
    },
    {
        "name": "DSLR Body — Full Frame",
        "description": "Reliable full-frame DSLR body, great low-light performance, comes with two spare batteries.",
        "category": "Camera Bodies",
        "price": 4000,
        "pricing_unit": Resource.PricingUnit.DAILY,
        "security_deposit": 25000,
        "location": "Nairobi Yard",
        "image_seed": "dslr-body-fullframe",
    },
    {
        "name": "24-70mm f/2.8 Zoom Lens",
        "description": "Standard fast zoom, the workhorse lens for events, portraits, and run-and-gun shoots.",
        "category": "Lenses",
        "price": 2000,
        "pricing_unit": Resource.PricingUnit.DAILY,
        "security_deposit": 15000,
        "location": "Nairobi Yard",
        "image_seed": "lens-24-70mm",
    },
    {
        "name": "70-200mm f/2.8 Telephoto Lens",
        "description": "Fast telephoto zoom for sports, wildlife, and compressed portrait work.",
        "category": "Lenses",
        "price": 2500,
        "pricing_unit": Resource.PricingUnit.DAILY,
        "security_deposit": 18000,
        "location": "Nairobi Yard",
        "image_seed": "lens-70-200mm",
    },
    {
        "name": "35mm f/1.4 Prime Lens",
        "description": "Wide-aperture prime for low light and shallow depth of field, popular for documentary work.",
        "category": "Lenses",
        "price": 1500,
        "pricing_unit": Resource.PricingUnit.DAILY,
        "security_deposit": 10000,
        "location": "Nairobi Yard",
        "image_seed": "lens-35mm-prime",
    },
    {
        "name": "3-Axis Gimbal Stabilizer",
        "description": "Handheld motorized gimbal for smooth, cinematic camera movement. Supports most mirrorless/DSLR bodies.",
        "category": "Support & Stabilization",
        "price": 2500,
        "pricing_unit": Resource.PricingUnit.DAILY,
        "security_deposit": 12000,
        "location": "Ruiru Yard",
        "image_seed": "gimbal-stabilizer-3axis",
    },
    {
        "name": "Carbon Fiber Tripod",
        "description": "Lightweight carbon fiber tripod with a fluid head, rated for both photo and video work.",
        "category": "Support & Stabilization",
        "price": 800,
        "pricing_unit": Resource.PricingUnit.DAILY,
        "security_deposit": 4000,
        "location": "Ruiru Yard",
        "image_seed": "tripod-carbon-fiber",
    },
    {
        "name": "LED Continuous Lighting Kit (2-Head)",
        "description": "Two bi-color LED panels with stands and softboxes, dimmable and battery- or mains-powered.",
        "category": "Lighting",
        "price": 3000,
        "pricing_unit": Resource.PricingUnit.DAILY,
        "security_deposit": 15000,
        "location": "Ruiru Yard",
        "image_seed": "led-lighting-kit-2head",
    },
    {
        "name": "Shotgun Mic + Field Recorder",
        "description": "Camera-mount shotgun microphone paired with a portable multi-track field recorder.",
        "category": "Audio",
        "price": 1500,
        "pricing_unit": Resource.PricingUnit.DAILY,
        "security_deposit": 8000,
        "location": "Nairobi Yard",
        "image_seed": "shotgun-mic-field-recorder",
    },
    {
        "name": "Camera Drone (4K)",
        "description": "Foldable 4K camera drone with obstacle avoidance and 30-minute flight time. Two spare batteries included.",
        "category": "Drones",
        "price": 6000,
        "pricing_unit": Resource.PricingUnit.DAILY,
        "security_deposit": 40000,
        "location": "Nairobi Yard",
        "image_seed": "camera-drone-4k",
    },
]


class Command(BaseCommand):
    help = "Seeds ~10 sample camera/photography equipment resources for local dev."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing seeded resources before re-creating them.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            deleted, _ = Resource.objects.filter(
                name__in=[item["name"] for item in EQUIPMENT]
            ).delete()
            if deleted:
                self.stdout.write(f"Removed {deleted} previously seeded resource(s).")

        created_count = 0
        skipped_count = 0

        for item in EQUIPMENT:
            image_seed = item.pop("image_seed")
            image_url = f"https://picsum.photos/seed/{image_seed}/800/600"

            resource, created = Resource.objects.get_or_create(
                name=item["name"],
                defaults={
                    **item,
                    "resource_type": Resource.ResourceType.EQUIPMENT,
                    "image_url": image_url,
                    "is_active": True,
                },
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created: {resource.name}"))
            else:
                skipped_count += 1
                self.stdout.write(f"Already exists, skipped: {resource.name}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Created {created_count}, skipped {skipped_count} "
                f"(already present)."
            )
        )
