from re import compile as re_compile
from dataclasses import dataclass


line_regexp = re_compile(r'(\s*)(?:([\w0-9.]+)\s+)?(\w+)@(\w+)(?:\s+([\w0-9.]+))?\s*')


@dataclass
class Line:
    level: int
    name: str
    type: str
    backward: str
    forward: str


class ColdLineParser:
    def __init__(self, level_marker_length: int = None):
        self._level_marker_length = level_marker_length

    def parse_line(self, line: str):
        match = line_regexp.fullmatch(line)

        indentation, backward_link_type, name, type_, forward_link_type = match.groups()

        indentation_length = len(indentation)
        level_index = 0

        level_marker_length = self._level_marker_length

        if indentation_length > 0:
            if level_marker_length is None:
                self._level_marker_length = indentation_length
                level_index = 1
            else:
                level_index = indentation_length // level_marker_length

                if indentation_length % level_marker_length > 0:
                    raise ValueError(f'Line indentation is not compatible with marker length = {self._level_marker_length}')

        return Line(level = level_index, name = name, type = type_, backward = backward_link_type, forward = forward_link_type)
