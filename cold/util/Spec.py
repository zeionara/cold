from .file import read, Format

from .type import infer_type, Type, INT_TYPE, FLOAT_TYPE

from .ColdLineParser import ColdLineParser, Line
from .NodeFactory import NodeFactory
from .NodeRegistry import NodeRegistry


reserved_values = {t.value for t in Type}


class Spec:
    def __init__(self, path: str, directed: bool = True):
        self.data = data = read(path)

        sources = set(data.keys())

        types = {}
        node_types = set()

        for source, config in data.items():
            node_types.add(source)

            if (links := config.get('link')) is not None:
                for destination, link_types in links.items():
                    assert destination in sources, f'Unknown destination type {destination}'

                    if isinstance(link_types, (list, tuple, set)):
                        types[(source, destination)] = set(link_types)
                    elif isinstance(link_types, str):
                        types[(source, destination)] = {link_types}
                    elif isinstance(link_types, dict):
                        raise ValueError('Nested type definitions are not allowed')
                    else:
                        raise ValueError(f'Invalid type spec: {type(link_types)}')

        self.factory = NodeFactory.from_types(node_types)

        # print(factory.make('foo', 'user'))

        self.types = types
        self.line_parser = ColdLineParser()
        self.directed = directed

    def validate(self, lhs: Line, rhs: Line, value: str):
        inferred_allowed_link_types_list = False

        # 1. Preprocess passed link

        value_type = infer_type(value)

        # 2. Check preprocessing results against the spec

        def compress(line: Line):
            return (line.name, line.type)

        def make_triple(lhs: Line, rhs: Line):
            nonlocal inferred_allowed_link_types_list

            if (allowed_types := self.types.get((lhs.type, rhs.type))) is not None:
                inferred_allowed_link_types_list = True

                if value_type == Type.STRING and value not in reserved_values and value in allowed_types:
                    return (compress(lhs), value, compress(rhs))
                if value_type == Type.INT and INT_TYPE in allowed_types:
                    return (compress(lhs), int(value), compress(rhs))
                if value_type == Type.FLOAT and FLOAT_TYPE in allowed_types:
                    return (compress(lhs), float(value), compress(rhs))

        if (triple := make_triple(lhs = lhs, rhs = rhs)) is not None:
            return triple

        if (triple := make_triple(lhs = rhs, rhs = lhs)) is not None:
            return triple

        if inferred_allowed_link_types_list:
            raise ValueError(f'Value {value} is not allowed between {lhs.type} and {rhs.type}')
        raise ValueError(f'Cannot infer allowed values between {lhs.type} and {rhs.type}')

    def handle(self, file, context: list = None, line: Line = None):
        if context is None:
            context = []

        # corpus = []
        corpus = NodeRegistry(self.factory, directed = self.directed)

        while True:
            if line is None:
                input_line = file.readline()

                if not input_line:
                    break

                line = self.line_parser.parse_line(input_line)

            if len(context) < 1:
                context.append(line)
                line = None
            else:
                if (last_line := context[-1]).level < line.level:
                    context.append(line)

                    if line.backward is None:
                        if last_line.forward is None:
                            raise ValueError('Cannot infer connection type')
                        # corpus.append(self.validate(last_line, line, last_line.forward))
                        corpus.push(self.validate(last_line, line, last_line.forward))
                    else:
                        # corpus.append(self.validate(last_line, line, line.backward))
                        corpus.push(self.validate(last_line, line, line.backward))

                    line = None
                else:
                    updated_context = []

                    for item in context:
                        if item.level < line.level:
                            updated_context.append(item)
                        else:
                            break

                    context = updated_context

        # return tuple(corpus)
        return corpus.cache

    def read(self, path: str):
        assert Format.from_path(path) == Format.COLD

        self._level_marker_length = None

        with open(path, 'r', encoding = 'utf-8') as file:
            return self.handle(file)
