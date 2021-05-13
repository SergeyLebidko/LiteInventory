from django import template

register = template.Library()


def dot(value):
    return str(value).replace(',', '.')


register.filter('dot', dot)
