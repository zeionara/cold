from unittest import TestCase, main

from cold.util import Spec


class TestDataReading(TestCase):

    def test_valid_one_type_config(self):
        Spec('assets/test/one-type.yml')

    def test_one_type_config_usage(self):
        assert Spec('assets/test/one-type.yml').read('assets/test/one-type-data.cld') == (('aaa', 'baz', 'bbb'), ('aaa', 'bar', 'ccc'))

    def test_one_type_config_invalid_link(self):
        with self.assertRaises(ValueError) as context:
            Spec('assets/test/one-type.yml').read('assets/test/one-type-data-missing-link-type-definition.cld')

        assert 'Link type bam is not allowed between foo and foo' in context.exception.args

    def test_one_type_config_invalid_node_types(self):
        with self.assertRaises(ValueError) as context:
            Spec('assets/test/two-types.yml').read('assets/test/two-types-data-invalid-node-types.cld')

        assert 'Cannot infer allowed link types between foo and foo' in context.exception.args

    def test_invalid_one_type_config(self):
        with self.assertRaises(AssertionError) as context:
            Spec('assets/test/one-type-missing-type-definition.yml')

        assert 'Unknown destination type bar' in context.exception.args


if __name__ == '__main__':
    main()
