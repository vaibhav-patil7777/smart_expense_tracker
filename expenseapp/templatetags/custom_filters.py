from django import template

register = template.Library()

@register.filter
def to_range(start, end):
    return range(start, end + 1)

@register.filter
def split_by(value, delimiter=","):
    return value.split(delimiter)

@register.filter
def index(sequence, i):
    try:
        return sequence[i - 1]
    except:
        return ''
