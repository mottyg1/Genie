import jinja2

import genie.filters
from genie.representation.expression import expressionize_dict

from genie.loaders import GenieLoader


class GenieEnvironment:

    def __init__(self, path, *args, **kwargs):
        self.queries_dialect = {}
        self.env = jinja2.Environment(loader=GenieLoader(path, self.queries_dialect), *args,
                                      **kwargs)
        self.env.filters = {**self.env.filters, **genie.filters.DEFAULT_FILTERS}

    def render(self, query_name, props):
        template = self.env.get_template(query_name)
        dialect = self.queries_dialect[query_name]
        props_expressions = expressionize_dict(props, dialect)
        return template.render(props_expressions)
