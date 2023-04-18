from unittest import TestCase, main

from cold.util import Spec


class TestDataReading(TestCase):

    def test_valid_one_type_config(self):
        Spec('assets/test/one-type.yml')

    def test_invalid_one_type_config(self):
        with self.assertRaises(AssertionError) as context:
            Spec('assets/test/one-type-missing-type-definition.yml')

        assert 'Unknown destination type bar' in context.exception.args


if __name__ == '__main__':
    main()
