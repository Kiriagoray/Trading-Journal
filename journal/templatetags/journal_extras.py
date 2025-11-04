from django import template

register = template.Library()

@register.simple_tag
def get_dynamic_fields(form):
    """Get fields that are not in the model's Meta.fields"""
    standard_fields = set(form.Meta.fields)
    dynamic = []
    for field_name, field in form.fields.items():
        if field_name not in standard_fields:
            dynamic.append((field_name, field))
    return dynamic

@register.filter
def get_field(form, field_name):
    """Get a form field by name"""
    if field_name in form.fields:
        return form[field_name]
    return ''

