from django import template


def table_header(context, headers):
    return {
        'headers': headers,
    }

register = template.Library()
register.inclusion_tag('table_header.html', takes_context=True)(table_header)
