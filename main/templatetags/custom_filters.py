from django import template

register = template.Library()


def dot(value):
    return str(value).replace(',', '.')


def none(value):
    if value is None:
        return ''
    return value


register.filter('dot', dot)
register.filter('none', none)
