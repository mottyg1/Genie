from jinja2 import Environment
import json
import yaml
from copy import deepcopy
from pprint import pprint

env = Environment()

REPRESENTATION_FUNCTIONS = {
    "global": {
        "raw": lambda k, v: v
    },
    "elasticsearch": {
        "str": lambda k, v: '{{ "term": {{ "{key}": {{ "value": "{value}" }} }} }}'.format(key=k, value=v).replace('"',
                                                                                                                   '\\\"'),
        "match": lambda k, v: '{{ "match": {{ "{key}": {{ "value": "{value}" }} }} }}'.format(key=k, value=v).replace(
            '"', '\\\"'),
        "int": lambda k, v: '{{ "term": {{ "{key}": {{ "value": {value} }} }} }}'.format(key=k, value=v).replace('"',
                                                                                                                 '\\\"'),
        "list": lambda k, v: '{{ "terms": {{ "{key}": {value} }} }}'.format(key=k, value=json.dumps(v)).replace('"',
                                                                                                                '\\\"'),
        "dict": lambda k, v: '{{ "range": {{ "{key}": {{ "gt": "{value_from}", "lt": "{value_to}" }} }} }}'.format(
            key=k, value_from=v.get('from'), value_to=v.get('to')).replace('"', '\\\"')
    },
    "solr": {
        'str': lambda k, v: "{}: {}".format(k, v),
        'int': lambda k, v: "{}: {}".format(k, v),
        'list': lambda k, v: '{}: ({})'.format(k, " ".join(v)),
        'dict': lambda k, v: '{}: [{} TO {}]'.format(k, v.get('from', '*'), v.get('to', '*'))
    }
}


def match(expression):
    e = deepcopy(expression)
    e.representation_function = 'match'
    return e


def key(expression, new_key):
    e = deepcopy(expression)
    e.key = new_key
    return e


def raw(expression):
    e = deepcopy(expression)
    e.representation_function = 'raw'
    return e


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

        return representation_function(self.key, self.value)


def expressionize_dict(dict_, dialect):
    expressionized_dict = {}
    for k, v in dict_.items():
        expressionized_dict[k] = Expression(k, v, dialect)
    return expressionized_dict


env.filters['match'] = match
env.filters['key'] = key
env.filters['raw'] = raw

f = yaml.load(open('examples/elasticsearch.yaml'), Loader=yaml.FullLoader)

dialect = f['dialect']
props = f['props']
template = env.from_string(json.dumps(f['execution']))

exec = template.render(expressionize_dict(props, dialect))
print(json.dumps(json.loads(json.loads(exec)['body'])))

# req = {
#     'sources': ['a', 'b', 'c'],
#     'name': 'motty',
#     'start_time': {
#         'from': '2019-10-31 17:30:00.000',
#         'to': '2019-11-01 15:00:00.000'
#     }
# }
#
# template = Template('{{ sources }} AND {{ name }} AND {{ start_time }}')
#
# s = template.render(expressionize_dict(req, 'elasticsearch'))
#
# print(s)
