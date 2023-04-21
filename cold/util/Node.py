from __future__ import annotations

from typing import ClassVar
from dataclasses import dataclass


@dataclass
class Node:
    type: ClassVar[str] = None

    name: str
    links: dict

    def push(self, link_type, value: Node):
        if (values := self.links.get(link_type)) is None:
            self.links[link_type] = [value]
        elif value not in values:
            values.append(value)

        return self
