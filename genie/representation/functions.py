import json

from jinja2 import contextfunction

import genie


def raw(e):
    return str(e.value)


def match(e):
    bool_template = '{{ "bool": {{ "should": [{}] }} }}'
    template = '{{ "match": {{ "{key}": {{ "value": "{value}" }} }} }}'
    values = list(e.value)
    match_blocks = [template.format(key=e.key, value=v) for v in values]
    if len(match_blocks) == 1:
        return match_blocks[0]
    else:
        return bool_template.format(','.join(match_blocks))


solr_trans = str.maketrans({'"': r'\"',
                            "]": r"\]",
                            "[": r"\[",
                            ")": r"\)",
                            "(": r"\(",
                            "\\": r"\\"
                            })

DEFAULT_REPRESENTATION_FUNCTION = raw

REPRESENTATION_FUNCTIONS = {
    "elasticsearch": {
        "str": lambda e: '{{ "term": {{ "{key}": {{ "value": "{value}" }} }} }}'.format(key=e.key, value=e.value),
        "match": match,
        "int": lambda e: '{{ "term": {{ "{key}": {{ "value": {value} }} }} }}'.format(key=e.key, value=e.value),
        "list": lambda e: '{{ "terms": {{ "{key}": {value} }} }}'.format(key=e.key, value=json.dumps(e.value)),
        "dict": lambda e: '{{ "range": {{ "{key}": {{ "gt": "{value_from}", "lt": "{value_to}" }} }} }}'.format(
            key=e.key, value_from=e.value.get('from'), value_to=e.value.get('to'))
    },
    "solr": {
        'str': lambda e: "{}: {}".format(e.key, e.value),
        'int': lambda e: "{}: {}".format(e.key, e.value),
        'list': lambda e: '{}: ({})'.format(e.key, " ".join(['"{}"'.format(x.translate(solr_trans)) for x in e.value])),
        'dict': lambda e: '{}: [{} TO {}]'.format(e.key, e.value.get('from', '*'), e.value.get('to', '*'))
    }
}


@contextfunction
def finalize_default_dialect(ctx, e):
    if isinstance(e, genie.representation.expression.Expression):
        try:
            e.template_dialect = ctx.vars['genie'].dialect
        except Exception:
            e.template_dialect = None
    return e
