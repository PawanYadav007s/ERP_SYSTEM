# sales/templatetags/sales_filters.py
from django import template

register = template.Library()

@register.filter
def divide(value, arg):
    """Divides the value by the argument."""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
    
@register.simple_tag
def empty_rows(current_count, target_count=10):
    """Generate empty rows to reach target count"""
    rows_needed = max(0, target_count - current_count)
    return range(rows_needed)