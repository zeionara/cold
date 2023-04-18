from .file import read


# def validate(data: dict):
#     if (links := data.get('link')) is not None:
#         for (key,  in links:


class Spec:
    def __init__(self, path: str):
        self.data = data = read(path)

        sources = set(data.keys())

        types = {}

        for source, config in data.items():
            if (links := config.get('link')) is not None:
                for destination, link_types in links.items():
                    assert destination in sources, f'Unknown destination type {destination}'

                    types[(source, destination)] = set(link_types)

        self.types = types
