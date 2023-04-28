from typing import Iterable

from .util import Node, get_node_hash


class NodeSet:
    def __init__(self, items: Iterable[Node] = None):
        self.input_items = items

        if items is None:
            self.items = {}
        else:
            item_tuples = tuple(items)

            hashes = set(get_node_hash(item) for item in item_tuples)

            assert len(hashes) == len(item_tuples), 'There are multiple nodes with the same hash which is not allowed'

            self.items = {get_node_hash(item): item for item in list(item_tuples)}

    def __contains__(self, item: Node):
        return get_node_hash(item) in self.items

    def get_linked_node_hashes(self, nodes: tuple[Node], type_name_pairs: set = None):
        type_name_pair_to_rich_node = {get_node_hash(node): node for node in self.items.values()}
        initial_call = False

        if type_name_pairs is None:
            type_name_pairs = set()
            initial_call = True

        more_nodes = []

        for node in nodes:
            if initial_call and (node_hash := get_node_hash(node)) not in type_name_pairs:
                type_name_pairs.add(node_hash)

            if node.links is not None and len(node.links) > 0:
                for link in node.links:
                    for nnode in link.items:  # nnode stands for 'next node'
                        if (nnode.type, nnode.name) not in type_name_pairs:
                            type_name_pairs.add((nnode.type, nnode.name))
                            more_nodes.append(type_name_pair_to_rich_node[(nnode.type, nnode.name)])

        if len(more_nodes) > 0:
            self.get_linked_node_hashes(more_nodes, type_name_pairs)

        return type_name_pairs

    def push(self, item: Node):
        if (item_hash := get_node_hash(item)) not in self.items:
            self.items[item_hash] = item

    def __getitem__(self, item: Node):
        return self.items.get(get_node_hash(item))
