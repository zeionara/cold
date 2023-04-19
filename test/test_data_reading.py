from unittest import TestCase, main

from cold.util import Spec


class TestDataReading(TestCase):

    def test_valid_one_type_config(self):
        Spec('assets/test/one-type.yml')

    def test_one_type_config_usage(self):
        self.assertEqual(Spec('assets/test/one-type.yml').read('assets/test/one-type-data.cld'), (('aaa', 'baz', 'bbb'), ('aaa', 'bar', 'ccc')))

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
            Spec('assets/test/one-type-with-numeric-value.yml').read('assets/test/one-type-with-numeric-value-data.cld'),
            (('one', 17, 'two'), ('one', 18.0, 'three'), ('one', 'baz', 'four'))
        )

    def test_single_link_config(self):
        self.assertEqual(
            Spec('assets/test/single-type.yml').read('assets/test/single-type-data.cld'),
            (('one', 17.7, 'two'), ('one', 17.7, 'three'))
        )


if __name__ == '__main__':
    main()
