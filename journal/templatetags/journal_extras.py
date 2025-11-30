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

@register.filter
def get_field_errors(form, field_name):
    """Get errors for a specific form field"""
    if field_name in form.errors:
        return form.errors[field_name]
    return []

@register.simple_tag
def get_entry_field_value(entry, field):
    """Get the value for a specific custom field from an entry"""
    from ..utils import get_field_value_for_entry
    value_obj = get_field_value_for_entry(entry, field)
    if value_obj:
        return value_obj.get_value_display()
    return ''

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Get an item from a dictionary by key"""
    if dictionary and isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''

@register.simple_tag
def get_custom_filter_value(filters, field_name):
    """Get custom field filter value from filters dict"""
    key = f'custom_{field_name}'
    return filters.get(key, '') if filters else ''

@register.simple_tag
def get_custom_filter_min(filters, field_name):
    """Get custom field filter min value from filters dict"""
    key = f'custom_{field_name}_min'
    return filters.get(key, '') if filters else ''

@register.simple_tag
def get_custom_filter_max(filters, field_name):
    """Get custom field filter max value from filters dict"""
    key = f'custom_{field_name}_max'
    return filters.get(key, '') if filters else ''

@register.filter
def startswith(value, arg):
    """Check if a string starts with a given substring"""
    if value and arg:
        return str(value).startswith(str(arg))
    return False

