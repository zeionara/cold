from enum import Enum
from re import compile as re_compile

int_pattern = re_compile(r'-?[0-9]+')
float_pattern = re_compile(r'-?(?:[0-9]+)\.(?:[0-9]+)?')


class Type(Enum):
    INT = 'int'
    FLOAT = 'float'
    STRING = 'string'


def infer_type(arg: str):
    if int_pattern.fullmatch(arg) is not None:
        return Type.INT
    if float_pattern.fullmatch(arg) is not None:
        return Type.FLOAT
    return Type.STRING
