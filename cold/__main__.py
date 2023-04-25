from json import dumps
from click import group, argument, option

from .util import Spec, JSONEncoder


@group()
def main():
    pass


@main.command()
@argument('path', type = str)
@argument('spec', type = str)
@option('--undirected', '-u', is_flag = True)
def probe(path: str, spec: str, undirected: bool):
    # corpus = Spec(spec).read(path)

    spec = Spec(spec, directed = not undirected)

    print(dumps(spec.read(path), indent = 2, cls = JSONEncoder))
    # print(MyEncoder().encode(spec.read(path)))


if __name__ == '__main__':
    main()
