from json import JSONEncoder as DefaultJSONEncoder  # , dumps
from unittest import TestCase, main

from cold.util import Spec, JSONEncoder, NodeFactory, Node, Link
from cold.util.collection import argmax

# from cold.util.string import dedent
from textwrap import dedent


def get_max_linked_node(nodes: list[Node], all_nodes: tuple[Node]):
    max_linked_node = argmax(nodes, lambda node: 0 if node.links is None else sum(len(link.items) for link in node.links))

    type_name_pairs = set() if max_linked_node.links is None or len(max_linked_node.links) < 1 else set((node.type, node.name) for link in max_linked_node.links for node in link.items)

    type_name_pair_to_rich_node = {(node.type, node.name): node for node in all_nodes}

    if max_linked_node.links is not None:
        for link in max_linked_node.links:
            link.items = tuple(type_name_pair_to_rich_node[(node.type, node.name)] for node in link.items)

    type_name_pairs.add((max_linked_node.type, max_linked_node.name))

    return max_linked_node, [node for node in nodes if (node.type, node.name) not in type_name_pairs]


def get_max_linked_link(node: Node):
    if node.links is None:
        return None, None

    max_linked_link = argmax(node.links, lambda link: len(link.items))
    links = [link_ for link_ in node.links if link_ != max_linked_link]

    return max_linked_link, links


def encode_node(node: Node, all_nodes: tuple[Node], link: Link = None, indent: int = 4, level: int = 0):
    indentation_first_line = ' ' * indent * level

    if link is None:
        return f'{indentation_first_line}{node.name}@{node.type}'

    # indentation = ' ' * indent * (level + 1)

    return f'{indentation_first_line}{node.name}@{node.type} {link.name}' + ''.join(f'\n{encode([node], all_nodes, indent, level + 1)}' for node in link.items)


def encode(nodes: list[Node], all_nodes: tuple[Node] = None, indent: int = 4, level: int = 0):
    if all_nodes is None:
        all_nodes = tuple(nodes)

    node, nodes = get_max_linked_node(nodes, all_nodes)
    link, links = get_max_linked_link(node)

    if link is None:
        return encode_node(node, all_nodes, link, indent, level)

    if len(links) > 0:
        raise ValueError(f'More than one link is not supported: {links}')

    # if len(nodes) > 0:
    #     raise ValueError(f'More than one node is not supported: {nodes}')

    return encode_node(node, all_nodes, link, indent, level) + ('' if len(nodes) < 1 else '\n' + encode(nodes, all_nodes, indent, level))


class TestDataReading(TestCase):

    def setUp(self):
        self.encoder = JSONEncoder()
        self.default_encoder = DefaultJSONEncoder()

    def test_cold_file_generation_multiple_first_level_nodes(self):
        factory = NodeFactory.from_types({'foo', 'bar'})

        one = factory.make('one', 'foo')
        two = factory.make('two', 'foo')

        three = factory.make('three', 'bar')

        four = factory.make('four', 'foo')
        five = factory.make('five', 'bar')

        one.push('qux', two)
        one.push('qux', three)

        two.push('qux', three)

        four.push('quux', five)

        nodes = [five, four, three, two, one]

        self.assertEqual(
            encode(nodes),
            dedent(
                """
                one@foo qux
                    two@foo qux
                        three@bar
                    three@bar
                four@foo quux
                    five@bar
                """
            ).strip()
        )

    def test_cold_file_generation(self):
        factory = NodeFactory.from_types({'foo', 'bar'})

        one = factory.make('one', 'foo')
        two = factory.make('two', 'foo')

        three = factory.make('three', 'bar')

        one.push('qux', two)
        one.push('qux', three)

        two.push('qux', three)

        nodes = [three, two, one]

        self.assertEqual(
            encode(nodes),
            dedent(
                """
                one@foo qux
                    two@foo qux
                        three@bar
                    three@bar
                """
            ).strip()
        )

    def test_two_types_with_symmetric_link_in_undirected_graph(self):
        with self.assertRaises(ValueError) as context:
            Spec('assets/test/two-types-with-symmetric.yml', directed = False)

        assert 'Inverse link spec is not allowed for undirected graphs (see bar^rab)' in context.exception.args

    def test_two_types_with_symmetric_link(self):
        self.assertEqual(
            self.encoder.encode(Spec('assets/test/two-types-with-symmetric.yml').read('assets/test/two-types-single-link.cld')),
            self.default_encoder.encode(
                {
                    "nodes": [
                        {
                            "name": "one",
                            "type": "foo",
                            "links": [
                                {
                                    "name": "bar",
                                    "items": [
                                        {
                                            "name": "two",
                                            "type": "bar"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "name": "two",
                            "type": "bar",
                            "links": [
                                {
                                    "name": "rab",
                                    "items": [
                                        {
                                            "name": "one",
                                            "type": "foo"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            )
        )

    def test_conflicting_link_definitions(self):
        with self.assertRaises(ValueError) as context:
            Spec('assets/test/conflicting-link-definitions.yml')

        assert 'Cannot unambiguosly infer link direction between foo and bar for link types one' in context.exception.args

    def test_valid_one_type_config(self):
        Spec('assets/test/one-type.yml')

    def test_one_type_config_usage_undirected(self):
        # print(dumps(Spec('assets/test/one-type.yml', directed = False).read('assets/test/one-type-data.cld'), indent = 4, cls = JSONEncoder))
        self.assertEqual(
            self.encoder.encode(Spec('assets/test/one-type.yml', directed = False).read('assets/test/one-type-data.cld')),
            self.default_encoder.encode(
                {
                    'nodes': [
                        {
                            "name": "aaa",
                            "type": "foo",
                            "links": [
                                {
                                    "name": "baz",
                                    "items": [
                                        {
                                            "name": "bbb",
                                            "type": "foo"
                                        }
                                    ]
                                },
                                {
                                    "name": "bar",
                                    "items": [
                                        {
                                            "name": "ccc",
                                            "type": "foo"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "name": "bbb",
                            "type": "foo",
                            "links": [
                                {
                                    "name": "baz",
                                    "items": [
                                        {
                                            "name": "aaa",
                                            "type": "foo"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "name": "ccc",
                            "type": "foo",
                            "links": [
                                {
                                    "name": "bar",
                                    "items": [
                                        {
                                            "name": "aaa",
                                            "type": "foo"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            )
        )

    def test_one_type_config_usage(self):
        # print(dumps(Spec('assets/test/one-type.yml', directed = False).read('assets/test/one-type-data.cld'), indent = 4, cls = JSONEncoder))
        self.assertEqual(
            self.encoder.encode(Spec('assets/test/one-type.yml').read('assets/test/one-type-data.cld')),
            self.default_encoder.encode(
                {
                    'nodes': [
                        {
                            "name": "aaa",
                            "type": "foo",
                            "links": [
                                {
                                    "name": "baz",
                                    "items": [
                                        {
                                            "name": "bbb",
                                            "type": "foo"
                                        }
                                    ]
                                },
                                {
                                    "name": "bar",
                                    "items": [
                                        {
                                            "name": "ccc",
                                            "type": "foo"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "name": "bbb",
                            "type": "foo"
                        },
                        {
                            "name": "ccc",
                            "type": "foo"
                        }
                    ]
                }
            )
        )

    def test_one_type_config_invalid_link(self):
        with self.assertRaises(ValueError) as context:
            Spec('assets/test/one-type.yml').read('assets/test/one-type-data-missing-link-type-definition.cld')

        self.assertIn('Value bam is not allowed between foo and foo', context.exception.args)

    def test_one_type_config_invalid_node_types(self):
        with self.assertRaises(ValueError) as context:
            Spec('assets/test/two-types.yml').read('assets/test/two-types-data-invalid-node-types.cld')

        self.assertIn('Cannot infer allowed values between foo and foo', context.exception.args)

    def test_invalid_one_type_config(self):
        with self.assertRaises(AssertionError) as context:
            Spec('assets/test/one-type-missing-type-definition.yml')

        self.assertIn('Unknown destination type bar', context.exception.args)

    def test_numeric_data_parsing(self):
        # print(dumps(Spec('assets/test/one-type-with-numeric-value.yml').read('assets/test/one-type-with-numeric-value-data.cld'), indent = 4, cls = JSONEncoder))
        self.assertEqual(
            self.encoder.encode(Spec('assets/test/one-type-with-numeric-value.yml').read('assets/test/one-type-with-numeric-value-data.cld')),
            self.default_encoder.encode(
                {
                    "nodes": [
                        {
                            "name": "one",
                            "type": "foo",
                            "links": [
                                {
                                    "name": 17,
                                    "items": [
                                        {
                                            "name": "two",
                                            "type": "foo"
                                        }
                                    ]
                                },
                                {
                                    "name": 18.0,
                                    "items": [
                                        {
                                            "name": "three",
                                            "type": "foo"
                                        }
                                    ]
                                },
                                {
                                    "name": "baz",
                                    "items": [
                                        {
                                            "name": "four",
                                            "type": "foo"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "name": "two",
                            "type": "foo"
                        },
                        {
                            "name": "three",
                            "type": "foo"
                        },
                        {
                            "name": "four",
                            "type": "foo"
                        }
                    ]
                }
            )
        )

    def test_single_link_config(self):
        # print(dumps(Spec('assets/test/single-type.yml').read('assets/test/single-type-data.cld'), indent = 4, cls = JSONEncoder))
        self.assertEqual(
            self.encoder.encode(Spec('assets/test/single-type.yml').read('assets/test/single-type-data.cld')),
            self.default_encoder.encode(
                {
                    "nodes": [
                        {
                            "name": "one",
                            "type": "foo",
                            "links": [
                                {
                                    "name": 17.7,
                                    "items": [
                                        {
                                            "name": "two",
                                            "type": "foo"
                                        },
                                        {
                                            "name": "three",
                                            "type": "foo"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "name": "two",
                            "type": "foo"
                        },
                        {
                            "name": "three",
                            "type": "foo"
                        }
                    ]
                }
            )
        )


if __name__ == '__main__':
    main()
