from __future__ import annotations

from typing import ClassVar
from dataclasses import dataclass


@dataclass
class Link:
    name: any
    items: list[str]

    @property
    def as_dict(self):
        return {
            'name': self.name,
            'items': tuple(self.items)
        }


@dataclass
class Node:
    type: ClassVar[str] = None

    name: str
    links: list = None

    def push(self, link_type, value: Node):
        for link in self.links:
            if link.name == link_type:
                for item in link.items:
                    if item.name == value.name:
                        break
                else:
                    link.items.append(value.clone_without_links())
                break
        else:
            self.links.append(Link(name = link_type, items = [value.clone_without_links()]))

        return self

    @property
    def as_dict(self):
        links = self.links

        if links is not None and len(links) > 0:
            return {
                'name': self.name,
                'type': self.type,
                'links': links
            }

        return {
            'name': self.name,
            'type': self.type
        }

    def clone_without_links(self):
        return type(self)(self.name)


def get_hash(node: Node):
    return (node.type, node.name)
