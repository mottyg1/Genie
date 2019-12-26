from genie.representation.functions import REPRESENTATION_FUNCTIONS


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