from copy import deepcopy
import json

DEFAULT_FILTERS = {}


def genie_filter(func):
    def wrapper_copy_expression(expression, *args, **kwargs):
        if not expression:
            return expression
        c = deepcopy(expression)
        func(c, *args, **kwargs)
        return c

    DEFAULT_FILTERS[func.__name__] = wrapper_copy_expression

    return wrapper_copy_expression


def register_jinja2_filter(func):
    DEFAULT_FILTERS[func.__name__] = func
    return func


@register_jinja2_filter
def dirty_json(line):
    while True:
        try:
            json.loads(line)  # try to parse...
            break  # parsing worked -> exit loop

        except Exception as e:
            if line[e.pos] == ',':  # preceding comma
                line = line[:e.pos] + line[e.pos + 1:]

            elif line[e.pos] in [']', '}']:  # trailing comma
                bad_comma = line[:e.pos].rfind(',')
                line = line[:bad_comma] + line[bad_comma + 1:]

            else:
                raise e

    return line


@genie_filter
def match(expression):
    expression.representation_function = 'match'


@genie_filter
def key(expression, new_key):
    expression.key = new_key


@genie_filter
def raw(expression):
    expression.representation_function = 'raw'
