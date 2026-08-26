from django import forms
from django.utils.html import escape
from django.utils.safestring import mark_safe


class DatalistTextInput(forms.TextInput):
    """
    A plain text input backed by an HTML <datalist>.

    Staff get a dropdown of existing values to pick from (fast, consistent
    spelling) but can still type something new if this is the first of its
    kind — unlike a hard <select>, it never blocks adding a new category or
    location.
    """

    def __init__(self, choices=(), attrs=None):
        super().__init__(attrs)
        self.choices = list(choices)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        list_id = f"{context['widget']['attrs'].get('id', name)}__list"
        context["widget"]["attrs"]["list"] = list_id
        context["widget"]["attrs"].setdefault(
            "autocomplete", "off"
        )
        context["list_id"] = list_id
        context["choices"] = self.choices
        return context

    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        context = self.get_context(name, value, attrs or {})
        options = "".join(
            f'<option value="{escape(choice)}">' for choice in context["choices"]
        )
        datalist = f'<datalist id="{context["list_id"]}">{options}</datalist>'
        return mark_safe(str(html) + datalist)
