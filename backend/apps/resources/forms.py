from django import forms

from .models import Resource

NORMALIZED_FIELDS = ("category", "location")


class ResourceAdminForm(forms.ModelForm):
    """
    Prevents "Camera kit" / "camera Kit" from becoming two different
    categories. If what staff typed matches an existing category or
    location except for case, we quietly reuse the existing spelling
    instead of creating a near-duplicate.

    Genuinely new values still go through untouched -- this only kicks in
    when a case-insensitive match already exists.
    """

    class Meta:
        model = Resource
        fields = "__all__"

    def _fold_to_existing_casing(self, field_name):
        value = self.cleaned_data.get(field_name)
        if not value:
            return value

        existing_match = (
            Resource.objects.exclude(pk=self.instance.pk)
            .filter(**{f"{field_name}__iexact": value})
            .exclude(**{field_name: value})  # already exact, nothing to fold
            .values_list(field_name, flat=True)
            .first()
        )
        return existing_match or value

    def clean_category(self):
        return self._fold_to_existing_casing("category")

    def clean_location(self):
        return self._fold_to_existing_casing("location")
