from typing import Iterable


def argmax(items: Iterable, get_value: callable):
    max_item = None
    max_value = None

    for item in items:
        value = get_value(item)

        if max_value is None or value > max_value:
            max_value = value
            max_item = item

    return max_item
