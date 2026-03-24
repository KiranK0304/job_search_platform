from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Look up a key in a dictionary. Usage: {{ mydict|get_item:key }}"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
