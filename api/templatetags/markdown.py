import markdown as md

from . import register


@register.filter
def markdown(value):
    return md.markdown(value)
