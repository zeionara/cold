from unittest import TestCase
from textwrap import dedent

from cold.util import NodeFactory, Spec
from cold import Encoder


class TestDataEncoding(TestCase):

    def test_cold_file_generation_multiple_node_mentions(self):
        factory = NodeFactory.from_types({'foo', 'bar'})

        one = factory.make('one', 'foo')
        two = factory.make('two', 'foo')

        three = factory.make('three', 'bar')

        four = factory.make('four', 'foo')
        five = factory.make('five', 'bar')

        one.push('qux', two)
        one.push('qux', three)

        two.push('qux', three)

        one.push('quux', four)

        four.push('quuz', five)
        five.push('quuz', two)

        nodes = [five, four, three, two, one]

        self.assertEqual(
            Encoder(nodes).encode(),
            dedent(
                """
                one@foo qux
                    two@foo qux
                        three@bar
                    three@bar
                    quux four@foo quuz
                        five@bar quuz
                            two@foo
                """
            ).strip()
        )

    def test_cold_file_generation_deep_node_mention(self):
        factory = NodeFactory.from_types({'foo', 'bar'})

        one = factory.make('one', 'foo')
        two = factory.make('two', 'foo')

        three = factory.make('three', 'bar')

        four = factory.make('four', 'foo')
        five = factory.make('five', 'bar')

        six = factory.make('six', 'foo')
        seven = factory.make('seven', 'foo')

        one.push('qux', two)
        one.push('qux', three)

        two.push('qux', three)

        one.push('quux', four)

        four.push('quuz', five)
        five.push('quuz', six)

        six.push('qux', seven)

        nodes = [seven, six, five, four, three, two, one]

        self.assertEqual(
            Encoder(nodes).encode(),
            dedent(
                """
                one@foo qux
                    two@foo qux
                        three@bar
                    three@bar
                    quux four@foo quuz
                        five@bar quuz
                            six@foo qux
                                seven@foo
                """
            ).strip()
        )

    def test_graph_validation(self):
        factory = NodeFactory.from_types({'foo', 'bar'})

        one = factory.make('one', 'foo')
        two = factory.make('two', 'foo')

        three = factory.make('three', 'bar')

        four = factory.make('four', 'foo')
        five = factory.make('five', 'bar')

        one.push('qux', two)
        one.push('qux', three)

        two.push('qux', three)

        one.push('quux', four)

        four.push('quuz', five)
        five.push('quuf', four)

        nodes = [five, four, three, two, one]

        spec = Spec(
            data = {
                'foo': {
                    'help': 'Some data type',
                    'link': {
                        'foo': [
                            'qux',
                            'quux'
                        ],
                        'bar': [
                            'qux',
                            'quuz'
                        ]
                    }
                },
                'bar': {}
            }
        )

        with self.assertRaises(ValueError) as context:
            Encoder(nodes, spec = spec).encode()

        assert 'Value quuf is not allowed between bar and foo' in context.exception.args

    def test_cold_file_generation_multiple_first_level_links_recursion_undirected(self):
        factory = NodeFactory.from_types({'foo', 'bar'})

        one = factory.make('one', 'foo')
        two = factory.make('two', 'foo')

        three = factory.make('three', 'bar')

        four = factory.make('four', 'foo')
        five = factory.make('five', 'bar')

        one.push('qux', two)
        one.push('qux', three)

        two.push('qux', three)

        one.push('quux', four)

        four.push('quuz', five)
        five.push('quuz', four)

        nodes = [five, four, three, two, one]

        # print(Encoder(nodes, directed = False).encode())

        self.assertEqual(
            Encoder(nodes, directed = False).encode(),
            dedent(
                """
                one@foo qux
                    two@foo qux
                        three@bar
                    three@bar
                    quux four@foo quuz
                        five@bar
                """
            ).strip()
        )

    def test_cold_file_generation_multiple_first_level_links_recursion_directed(self):
        factory = NodeFactory.from_types({'foo', 'bar'})

        one = factory.make('one', 'foo')
        two = factory.make('two', 'foo')

        three = factory.make('three', 'bar')

        four = factory.make('four', 'foo')
        five = factory.make('five', 'bar')

        one.push('qux', two)
        one.push('qux', three)

        two.push('qux', three)

        one.push('quux', four)

        four.push('quuz', five)
        five.push('quuz', four)

        nodes = [five, four, three, two, one]

        self.assertEqual(
            Encoder(nodes).encode(),
            dedent(
                """
                one@foo qux
                    two@foo qux
                        three@bar
                    three@bar
                    quux four@foo quuz
                        five@bar quuz
                            four@foo
                """
            ).strip()
        )

    def test_cold_file_generation_multiple_first_level_links(self):
        factory = NodeFactory.from_types({'foo', 'bar'})

        one = factory.make('one', 'foo')
        two = factory.make('two', 'foo')

        three = factory.make('three', 'bar')

        four = factory.make('four', 'foo')
        five = factory.make('five', 'bar')

        one.push('qux', two)
        one.push('qux', three)

        two.push('qux', three)

        one.push('quux', four)

        four.push('quuz', five)

        nodes = [five, four, three, two, one]

        self.assertEqual(
            Encoder(nodes).encode(),
            dedent(
                """
                one@foo qux
                    two@foo qux
                        three@bar
                    three@bar
                    quux four@foo quuz
                        five@bar
                """
            ).strip()
        )

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
            Encoder(nodes).encode(),
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
            Encoder(nodes).encode(),
            dedent(
                """
                one@foo qux
                    two@foo qux
                        three@bar
                    three@bar
                """
            ).strip()
        )
