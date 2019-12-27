import json


def raw(expression):
    return str(expression.value)


REPRESENTATION_FUNCTIONS = {
    "global": {
        "str": raw,
        "int": raw,
        "list": raw,
        "dict": raw,
        "raw": raw,
        "empty": lambda e: None
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



