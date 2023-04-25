from unittest import TestCase, main

from cold.util import Spec, JSONEncoder


class TestDataReading(TestCase):

    def setUp(self):
        self.encoder = JSONEncoder()

    def test_valid_one_type_config(self):
        Spec('assets/test/one-type.yml')

    def test_one_type_config_usage(self):
        self.assertEqual(
            self.encoder.encode(Spec('assets/test/one-type.yml').read('assets/test/one-type-data.cld')),
            '{"foo": {"aaa": {"name": "aaa", "links": {"baz": ["bbb"], "bar": ["ccc"]}}, "bbb": {"name": "bbb"}, "ccc": {"name": "ccc"}}}'
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
        self.assertEqual(
            self.encoder.encode(Spec('assets/test/one-type-with-numeric-value.yml').read('assets/test/one-type-with-numeric-value-data.cld')),
            '{"foo": {"one": {"name": "one", "links": {"17": ["two"], "18.0": ["three"], "baz": ["four"]}}, "two": {"name": "two"}, "three": {"name": "three"}, "four": {"name": "four"}}}'
        )

    def test_single_link_config(self):
        self.assertEqual(
            self.encoder.encode(Spec('assets/test/single-type.yml').read('assets/test/single-type-data.cld')),
            '{"foo": {"one": {"name": "one", "links": {"17.7": ["two", "three"]}}, "two": {"name": "two"}, "three": {"name": "three"}}}'
        )


if __name__ == '__main__':
    main()
