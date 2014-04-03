from django import template

register = template.Library()

def phone(value):
    result = ""
    if len(value) == 10:
        for i in range(2, 11, 2):
            result += value[i-2:i] + " "
        result = result[:-1]
    else:
        result = value
    return result

register.filter('phone', phone)
