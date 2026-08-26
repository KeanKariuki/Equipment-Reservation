from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe  # <-- Added mark_safe import

from .forms import ResourceAdminForm
from .models import Resource
from .widgets import DatalistTextInput


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    form = ResourceAdminForm

    list_display = (
        "thumbnail",
        "name",
        "category",
        "price",
        "pricing_unit",
        "is_active",
    )

    list_display_links = ("thumbnail", "name")

    # Staff can flip price/status right from the list without opening
    # each item -- handy for quick corrections or seasonal pricing.
    list_editable = ("price", "is_active")

    list_filter = (
        "resource_type",
        "pricing_unit",
        "is_active",
    )

    search_fields = (
        "name",
        "category",
        "location",
    )

    ordering = ("-created_at",)

    readonly_fields = ("photo_preview",)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        # Category and location stay free-text fields (so staff can always
        # add a brand-new one), but get a dropdown of existing values so
        # most of the time it's a pick, not a retype. Deduped case-
        # insensitively so old "Lenses"/"lenses" variants only show once.
        if db_field.name in ("category", "location"):
            raw_values = (
                Resource.objects.exclude(**{db_field.name: ""})
                .order_by(db_field.name)
                .values_list(db_field.name, flat=True)
            )
            seen_lower = set()
            existing = []
            for value in raw_values:
                key = value.lower()
                if key not in seen_lower:
                    seen_lower.add(key)
                    existing.append(value)
            kwargs["widget"] = DatalistTextInput(choices=existing)
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    fieldsets = (
        (
            "Item details",
            {
                "fields": (
                    "name",
                    "description",
                    "resource_type",
                    "category",
                    "location",
                ),
            },
        ),
        (
            "Photo",
            {
                "fields": ("photo_preview", "image", "image_url"),
                "description": (
                    "Upload a photo below \u2014 it will show up on the site right away. "
                    "\u201cLink to a photo\u201d is only used as a backup if no photo is uploaded."
                ),
            },
        ),
        (
            "Pricing",
            {
                "fields": ("price", "pricing_unit", "security_deposit"),
            },
        ),
        (
            "Status",
            {
                "fields": ("is_active",),
            },
        ),
    )

    @admin.display(description="Photo")
    def thumbnail(self, obj):
        if not obj or not getattr(obj, "photo_url", None):
            return mark_safe(  # <-- Fixed: replaced format_html with mark_safe
                '<div class="fm-thumb fm-thumb--empty">No photo</div>'
            )
        return format_html('<img src="{}" class="fm-thumb" />', obj.photo_url)

    @admin.display(description="Current photo")
    def photo_preview(self, obj):
        if not obj or not getattr(obj, "photo_url", None):
            return mark_safe(  # <-- Fixed: replaced format_html with mark_safe
                '<div class="fm-thumb fm-thumb--large fm-thumb--empty">No photo yet</div>'
            )
        return format_html(
            '<img src="{}" class="fm-thumb fm-thumb--large" />', obj.photo_url
        )

    class Media:
        css = {"all": ("admin/css/field_manual_admin.css",)}
        js = ("admin/js/resource_image_upload.js",)