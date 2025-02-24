from django import template
from datetime import time
from datetime import datetime
register = template.Library()

def custom_tag(value):
    # Perform desired logic
    result = value.upper()
    return result

def split(value):
    return value.split(',')

def total(value, diff):
    value = int(value)
    value = value/100 * diff+ value
    return value

@register.filter(name='is_before_time')
def is_before_time(current_time):
    current_time = datetime.now().time()
    specified_time = time(9,0,0)
    return current_time < specified_time

@register.filter
def slice_to_100(value):
    if len(value) > 100:
        return value[:100] + '...'  # Slice the string to a maximum of 200 characters and append ellipsis
    else:
        return value


register.filter('custom_tag', custom_tag)
register.filter('split', split)
register.filter('total', total)