from jinja2 import Environment
import json
import yaml
from copy import deepcopy

env = Environment()

REPRESENTATION_FUNCTIONS = {
    "global": {
        "raw": lambda e: e.value
    },
    "elasticsearch": {
        "str": lambda e: '{{ "term": {{ "{key}": {{ "value": "{value}" }} }} }}'.format(key=e.key, value=e.value),
        "match": lambda e: '{{ "match": {{ "{key}": {{ "value": "{value}" }} }} }}'.format(key=e.key, value=e.value),
        "int": lambda e: '{{ "term": {{ "{key}": {{ "value": {value} }} }} }}'.format(key=e.key, value=e.value),
        "list": lambda e: '{{ "terms": {{ "{key}": {value} }} }}'.format(key=e.key, value=json.dumps(e.value)),
        "dict": lambda e: '{{ "range": {{ "{key}": {{ "gt": "{value_from}", "lt": "{value_to}" }} }} }}'.format(
            key=e.key, value_from=e.value.get('from'), value_to=e.value.get('to'))
    },
    "solr": {
        'str': lambda e: "{}: {}".format(e.key, e.value),
        'int': lambda e: "{}: {}".format(e.key, e.value),
        'list': lambda e: '{}: ({})'.format(e.key, " ".join(e.value)),
        'dict': lambda e: '{}: [{} TO {}]'.format(e.key, e.value.get('from', '*'), e.value.get('to', '*'))
    }
}


def genie_filter(func):
    def wrapper_copy_expression(expression, *args, **kwargs):
        if not expression:
            return expression
        c = deepcopy(expression)
        func(c, *args, **kwargs)
        return c

    env.filters[func.__name__] = wrapper_copy_expression

    return wrapper_copy_expression


@genie_filter
def match(expression):
    expression.representation_function = 'match'


@genie_filter
def key(expression, new_key):
    expression.key = new_key


@genie_filter
def raw(expression):
    expression.representation_function = 'raw'


class Expression:

    def __init__(self, key, value, dialect):
        self.key = key
        self.value = value

        self.dialect = dialect
        self.representation_function = value.__class__.__name__

    def __repr__(self):
        representation_function = REPRESENTATION_FUNCTIONS[self.dialect].get(self.representation_function)
        if not representation_function:
            representation_function = REPRESENTATION_FUNCTIONS['global'][self.representation_function]

        return representation_function(self)


def expressionize_dict(dict_, dialect):
    expressionized_dict = {}
    for k, v in dict_.items():
        expressionized_dict[k] = Expression(k, v, dialect)
    return expressionized_dict


f = yaml.load(open('examples/elasticsearch.yaml'), Loader=yaml.FullLoader)

dialect = f['dialect']
props = f['props']
template = env.from_string(f['execution'])

exec = template.render(expressionize_dict(props, dialect))
print(yaml.full_load(exec))
# print(json.dumps(json.loads(json.loads(exec)['body'])))
# print(exec)
