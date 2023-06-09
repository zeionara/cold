from json import JSONEncoder as DefaultJSONEncoder  # , dumps
from unittest import TestCase, main

from cold.util import Spec, JSONEncoder


class TestDataReading(TestCase):

    def setUp(self):
        self.encoder = JSONEncoder()
        self.default_encoder = DefaultJSONEncoder()

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
