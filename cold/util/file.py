from enum import Enum

import yaml

from .string import get_extension


class Format(Enum):
    YAML = 'yaml'

    @staticmethod
    def from_path(path: str):
        extension = get_extension(path)

        if extension in ('yaml', 'yml'):
            return Format.YAML

        raise ValueError(f'Cannot infer file format from path: "{path}"')


def _read(path: str, format_: Format, /):
    match format_:
        case Format.YAML:
            with open(path, 'r', encoding = 'utf-8') as file:
                return yaml.safe_load(file)
        case _:
            raise ValueError(f'Unknown file format: {format_}')


def read(path: str):
    return _read(path, Format.from_path(path))
