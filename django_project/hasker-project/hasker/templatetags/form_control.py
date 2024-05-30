from django import template
from django.forms import BoundField

register = template.Library()


@register.filter
def form_control(input: BoundField):
    if not input.is_hidden:
        input.field.widget.attrs["class"] = "form-control"
    return input
