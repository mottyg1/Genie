import jinja2

import genie.filters
from genie.representation.expression import expressionize_dict

from jinja2.loaders import FileSystemLoader

from genie.representation.functions import finalize_default_dialect


class GenieEnvironment:

    def __init__(self, path, *args, **kwargs):
        self.env = jinja2.Environment(loader=FileSystemLoader(path), finalize=finalize_default_dialect, *args,
                                      **kwargs)
        self.env.filters = {**self.env.filters, **genie.filters.DEFAULT_FILTERS}

    def render(self, query_name, props):
        template = self.env.get_template(query_name)
        props_expressions = expressionize_dict(props)
        return template.render(props_expressions)
