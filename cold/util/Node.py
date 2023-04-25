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
            self.links[link_type] = [value.name]
        elif value not in values:
            values.append(value.name)

        return self

    @property
    def as_dict(self):
        items = self.links.items()

        if len(items) > 0:
            return {
                'name': self.name,
                'links': dict(items)
            }

        return {
            'name': self.name
        }
