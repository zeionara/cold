from .util import Node, Link
from .util.collection import argmax

from .NodeSet import NodeSet


SEP = ' '


class Encoder:
    def __init__(self, nodes: tuple[Node], indent: int = 4):
        self.nodes = NodeSet(nodes)
        self.defined_nodes = NodeSet()
        self.indent = indent

    def get_max_linked_node(self, nodes: list[Node]):
        max_linked_node = argmax(nodes, lambda node: 0 if node.links is None else sum(len(link.items) for link in node.links))

        type_name_pairs = self.nodes.get_linked_node_hashes([max_linked_node])  # collect_type_name_pairs([max_linked_node], all_nodes)

        if max_linked_node.links is not None:
            for link in max_linked_node.links:
                link.items = tuple(self.nodes[node] for node in link.items)

        return max_linked_node, [node for node in nodes if (node.type, node.name) not in type_name_pairs]

    def get_max_linked_link(self, node: Node):
        if node.links is None:
            return None, None

        max_linked_link = argmax(node.links, lambda link: len(link.items))
        links = [link_ for link_ in node.links if link_ != max_linked_link]

        return max_linked_link, links

    def encode_node(self, node: Node, link: Link = None, level: int = 0, links: tuple[Link] = None, prefix: str = None):
        indentation_first_line = SEP * self.indent * level
        indented_prefix = "" if prefix is None else (prefix + SEP)

        if link is None:
            return f'{indentation_first_line}{indented_prefix}{node.name}@{node.type}'

        def encode_node_(node, prefix: str = None):
            return f'\n{self.encode_node(node, level = level + 1, prefix = prefix) if node in self.defined_nodes else self.encode([node], level + 1, prefix = prefix)}'

        # if prefix is None:
        #     return (
        #         f'{indentation_first_line}{node.name}@{node.type} {link.name}' +
        #         ''.join(f'\n{encode_node(node, all_nodes, indent = indent, level = level + 1) if node in defined_nodes else encode([node], all_nodes, defined_nodes, indent, level + 1)}' for node in link.items) +
        #         ('' if links is None else ''.join(f'\n{encode_node(node, all_nodes, prefix = link.name, indent = indent, level = level + 1) if node in defined_nodes else encode([node], all_nodes, defined_nodes, indent, level + 1, link.name)}' for link in links for node in link.items if node not in defined_nodes))
        #     )
        return (
            f'{indentation_first_line}{indented_prefix}{node.name}@{node.type} {link.name}' +
            ''.join(encode_node_(node) for node in link.items) +
            ('' if links is None else ''.join(encode_node_(node, prefix = link.name) for link in links for node in link.items))
        )

    def encode(self, nodes: list[Node] = None, level: int = 0, prefix: str = None):
        if level > 10:
            raise ValueError('Too much nesting')

        if nodes is None:  # initial (non-recursive) call, reset state
            nodes = list(self.nodes.input_items)
            self.defined_nodes = NodeSet()

        node, nodes = self.get_max_linked_node(nodes)
        link, links = self.get_max_linked_link(node)

        if link is None:
            return self.encode_node(node, level = level, prefix = prefix)

        sorted_links = sorted(links, key = lambda lhs: len(link.items), reverse = True)

        self.defined_nodes.push(node)

        return self.encode_node(node, link, level, sorted_links, prefix) + ('' if len(nodes) < 1 else '\n' + self.encode(nodes, level, prefix))
