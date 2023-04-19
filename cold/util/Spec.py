from dataclasses import dataclass

from re import compile
from .file import read, Format


# def validate(data: dict):
#     if (links := data.get('link')) is not None:
#         for (key,  in links:

# line_regexp = compile(r'(\s*)(\w+)@(\w+)(?:\s+-(\w+))?(?:\s+\+(\w+))?\s*')
line_regexp = compile(r'(\s*)(?:(\w+)\s+)?(\w+)@(\w+)(?:\s+(\w+))?\s*')

# LEVEL_MARKER_LENGTH = None


@dataclass
class Line:
    level: int
    name: str
    type: str
    backward: str
    forward: str


class Spec:
    def __init__(self, path: str):
        self.data = data = read(path)

        sources = set(data.keys())

        types = {}

        for source, config in data.items():
            if (links := config.get('link')) is not None:
                for destination, link_types in links.items():
                    assert destination in sources, f'Unknown destination type {destination}'

                    types[(source, destination)] = set(link_types)

        self.types = types

        self._level_marker_length = None

    def parse_line(self, line):
        # global LEVEL_MARKER_LENGTH

        match = line_regexp.fullmatch(line)

        indentation, backward_link_type, name, type_, forward_link_type = match.groups()

        level_marker_length = len(indentation)
        level_index = 0

        if level_marker_length > 0:
            # if LEVEL_MARKER_LENGTH is None:
            if self._level_marker_length is None:
                # LEVEL_MARKER_LENGTH = level_marker_length
                self._level_marker_length = level_marker_length
                level_index = 1
            else:
                # level_index = level_marker_length // LEVEL_MARKER_LENGTH
                level_index = level_marker_length // self._level_marker_length

        return Line(level = level_index, name = name, type = type_, backward = backward_link_type, forward = forward_link_type)

    def validate(self, lhs: Line, rhs: Line, link_type: str):
        inferred_allowed_link_types_list = False

        if (allowed_types := self.types.get((lhs.type, rhs.type))) is not None:
            inferred_allowed_link_types_list = True

            if link_type in allowed_types:
                return (lhs.name, link_type, rhs.name)
        if (allowed_types := self.types.get((rhs.type, lhs.type))) is not None:
            inferred_allowed_link_types_list = True

            if link_type in allowed_types:
                return (rhs.name, link_type, lhs.name)

        if inferred_allowed_link_types_list:
            raise ValueError(f'Link type {link_type} is not allowed between {lhs.type} and {rhs.type}')
        raise ValueError(f'Cannot infer allowed link types between {lhs.type} and {rhs.type}')

    def handle(self, file, context: list = None, line: Line = None):
        if context is None:
            context = []

        corpus = []

        while True:
            if line is None:
                input_line = file.readline()

                if not input_line:
                    break

                line = self.parse_line(input_line)

            if len(context) < 1:
                context.append(line)
                line = None
            else:
                if (last_line := context[-1]).level < line.level:
                    context.append(line)

                    if line.backward is None:
                        if last_line.forward is None:
                            raise ValueError('Cannot infer connection type')
                        corpus.append(self.validate(last_line, line, last_line.forward))
                    else:
                        corpus.append(self.validate(last_line, line, line.backward))

                    line = None
                else:
                    updated_context = []

                    for item in context:
                        if item.level < line.level:
                            updated_context.append(item)
                        else:
                            break

                    context = updated_context

        return tuple(corpus)

    def read(self, path: str):
        assert Format.from_path(path) == Format.COLD

        self._level_marker_length = None

        with open(path, 'r', encoding = 'utf-8') as file:
            return self.handle(file)
