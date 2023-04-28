from .util import Node, Link, get_node_hash


def make_entry(lhs: Node, rhs: Node, link: Link):
    return (tuple(sorted([get_node_hash(lhs), get_node_hash(rhs)])), link.name)


class LinkSet:
    def __init__(self):
        self.items = set()

    def push(self, lhs: Node, rhs: Node, link: Link):
        self.items.add(make_entry(lhs = lhs, rhs = rhs, link = link))

    def contains(self, lhs: Node, rhs: Node, link: Link):
        return make_entry(lhs = lhs, rhs = rhs, link = link) in self.items
