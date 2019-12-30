from genie.representation.functions import REPRESENTATION_FUNCTIONS, DEFAULT_REPRESENTATION_FUNCTION
from genie.representation.exceptions import UnknownDialectException, UnknownRepresentationFunctionException


class Expression:

    def __init__(self, key, value, dialect=None):
        self.key = key
        self.value = value

        self.dialect = dialect
        self.template_dialect = None
        self.representation_function = value.__class__.__name__

    def __repr__(self):
        dialect = self.dialect if self.dialect else self.template_dialect

        if not dialect:
            return DEFAULT_REPRESENTATION_FUNCTION(self)

        if dialect not in REPRESENTATION_FUNCTIONS:
            raise UnknownDialectException('"{}" is not recognized as a valid dialect'.format(dialect))

        if self.representation_function not in REPRESENTATION_FUNCTIONS[dialect]:
            raise UnknownRepresentationFunctionException(
                '"{}" representation function for the "{}" dialect is not configured'.format(
                    self.representation_function, dialect))

        representation_function = REPRESENTATION_FUNCTIONS[dialect].get(self.representation_function,
                                                                        DEFAULT_REPRESENTATION_FUNCTION)

        return representation_function(self)

    def __iter__(self):
        return iter(self.value)


def expressionize_dict(dict_):
    expressionized_dict = {}
    for k, v in dict_.items():
        expressionized_dict[k] = Expression(k, v)
    return expressionized_dict
