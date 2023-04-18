from click import group, argument

from .util.file import read


@group()
def main():
    pass


@main.command()
@argument('path', type = str)
@argument('spec', type = str)
def probe(path: str, spec: str):
    print(read(spec))
    print(path, spec)


if __name__ == '__main__':
    main()
