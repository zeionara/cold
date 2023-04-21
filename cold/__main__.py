from click import group, argument

from .util import Spec


@group()
def main():
    pass


@main.command()
@argument('path', type = str)
@argument('spec', type = str)
def probe(path: str, spec: str):
    # corpus = Spec(spec).read(path)
    spec = Spec(spec)
    print(spec.read(path))


if __name__ == '__main__':
    main()
