from typing import Iterable
from .Node import Node


class NodeFactory:
    def __init__(self, node_classes: Iterable[Node]):
        type_to_node_class = {}

        for class_ in node_classes:
            assert (type_ := class_.type) is not None, f'Class {class_} has no associated string name'
            assert (type_to_node_class.get(type_)) is None, f'Key {class_.type} is used for identifying more than one class, which is forbidden'

            type_to_node_class[class_.type] = class_

        self._type_to_node_class = type_to_node_class

    @classmethod
    def from_types(cls, types: Iterable[str]):
        return cls(
            type(type_.capitalize(), (Node, ), {'type': type_})
            for type_ in types
        )

    def make(self, name: str, type_: str, /):
        return self._type_to_node_class[type_](name, {})
