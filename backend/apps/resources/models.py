from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]
MAX_IMAGE_SIZE_MB = 5


def validate_image_file_size(file):
    limit_bytes = MAX_IMAGE_SIZE_MB * 1024 * 1024
    if file.size > limit_bytes:
        raise ValidationError(f"Image must be under {MAX_IMAGE_SIZE_MB}MB.")


class Resource(models.Model):
    class ResourceType(models.TextChoices):
        EQUIPMENT = "equipment", "Equipment"
        SPACE = "space", "Space"

    class PricingUnit(models.TextChoices):
        HOURLY = "hour", "Per Hour"
        DAILY = "day", "Per Day"

    name = models.CharField(max_length=255)

    description = models.TextField()

    resource_type = models.CharField(
        max_length=20,
        choices=ResourceType.choices,
    )

    category = models.CharField(max_length=100)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    image = models.ImageField(
        upload_to="resources/%Y/%m/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_IMAGE_EXTENSIONS),
            validate_image_file_size,
        ],
        help_text=(
            "Upload a photo of this item (jpg, jpeg, png, or webp, under "
            f"{MAX_IMAGE_SIZE_MB}MB). Recommended: a clear shot on a plain "
            "background, landscape orientation."
        ),
    )

    image_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="Optional: link to a photo hosted elsewhere. Only used if no photo is uploaded above.",
    )

    pricing_unit = models.CharField(
        max_length=10,
        choices=PricingUnit.choices,
        default=PricingUnit.HOURLY,
    )

    security_deposit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    location = models.CharField(
        max_length=255,
        blank=True,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def photo_url(self):
        """The photo to show: an uploaded image takes priority over a linked one."""
        if self.image:
            return self.image.url
        return self.image_url or None