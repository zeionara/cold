from unittest import TestCase, main

from cold.util.type import infer_type, Type


class TestTypeInference(TestCase):

    def test_positive_int_inference(self):
        self.assertEqual(infer_type('17'), Type.INT)

    def test_negative_int_inference(self):
        self.assertEqual(infer_type('-17'), Type.INT)

    def test_positive_full_float_inference(self):
        self.assertEqual(infer_type('17.17'), Type.FLOAT)

    def test_negative_full_float_inference(self):
        self.assertEqual(infer_type('-17.17'), Type.FLOAT)

    def test_negative_full_float_inference_without_fractional_part(self):
        self.assertEqual(infer_type('-17.'), Type.FLOAT)

    def test_string_inference(self):
        self.assertEqual(infer_type('st'), Type.STRING)


if __name__ == '__main__':
    main()
