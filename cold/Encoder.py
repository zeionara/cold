from .util import Node, Link, Spec
from .util.collection import argmax

from .NodeSet import NodeSet
from .LinkSet import LinkSet


SEP = ' '


class UndirectedLink:
    def __init__(self, node: Node, base: Link, links: LinkSet):
        self.node = node
        self.base = base
        self.links = links

    @property
    def name(self):
        return self.base.name

    # @property
    # def items(self):
    #     return self.items

    @property
    def items(self):
        return tuple(item for item in self.base.items if not self.links.contains(lhs = self.node, rhs = item, link = self.base))


class Encoder:
    def __init__(self, nodes: tuple[Node], indent: int = 4, directed: bool = True, spec: Spec = None):
        self.nodes = NodeSet(nodes)
        self.defined_nodes = NodeSet()

        self.indent = indent

        self.directed = directed
        self.undirected = not directed

        self.links = None if directed else LinkSet()

        self.spec = spec

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

        if self.undirected:  # some links may have already appeared in a reversed representation
            non_zero_links = []

            for link in node.links:
                undirected_link = UndirectedLink(node = node, base = link, links = self.links)
                if len(undirected_link.items) > 0:
                    non_zero_links.append(undirected_link)

            node_links = non_zero_links
        else:
            node_links = node.links

        # print(self.undirected)
        # print(node_links)

        max_linked_link = argmax(node_links, lambda link: len(link.items))
        links = [link_ for link_ in node_links if link_ != max_linked_link]

        if self.undirected:
            return None if max_linked_link is None else max_linked_link.base, tuple(link.base for link in links)

        return max_linked_link, links

    def encode_node(self, node: Node, link: Link = None, level: int = 0, links: tuple[Link] = None, prefix: str = None):
        indentation_first_line = SEP * self.indent * level
        indented_prefix = "" if prefix is None else (prefix + SEP)

        if link is None:
            return f'{indentation_first_line}{indented_prefix}{node.name}@{node.type}'

        globalNode = node
        globalLink = link

        def encode_node_(node, link: Link = None):
            prefix = None if link is None else link.name

            if self.undirected:
                if self.links.contains(lhs = globalNode, rhs = node, link = globalLink if link is None else link):
                    return ''
                else:
                    self.links.push(lhs = globalNode, rhs = node, link = globalLink if link is None else link)

            if self.spec is not None:
                self.spec.validate(globalNode, node, (globalLink if link is None else link).name)

            return f'\n{self.encode_node(node, level = level + 1, prefix = prefix) if node in self.defined_nodes else self.encode([node], level + 1, prefix = prefix)}'

        return (
            f'{indentation_first_line}{indented_prefix}{node.name}@{node.type}{SEP}{link.name}' +
            ''.join(encode_node_(node) for node in link.items) +
            ('' if links is None else ''.join(encode_node_(node, link) for link in links for node in link.items))
        )

    def encode(self, nodes: list[Node] = None, level: int = 0, prefix: str = None):
        if level > 10:
            raise ValueError('Too much nesting')

        if nodes is None:  # initial (non-recursive) call, reset state
            nodes = list(self.nodes.input_items)
            self.defined_nodes = NodeSet()

        node, nodes = self.get_max_linked_node(nodes)
        link, links = self.get_max_linked_link(node)

        # print(link, links)

        if link is None:
            return self.encode_node(node, level = level, prefix = prefix)

        sorted_links = sorted(links, key = lambda lhs: len(link.items), reverse = True)

        self.defined_nodes.push(node)

        return self.encode_node(node, link, level, sorted_links, prefix) + ('' if len(nodes) < 1 else '\n' + self.encode(nodes, level, prefix))
