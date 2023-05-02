from json import dump, dumps
from click import group, argument, option

from .util import Spec, JSONEncoder, VkApi, MAX_BATCH_SIZE

from os import environ as env


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


@main.command()
@argument('community', type = str)
@option('--count', '-c', type = int, default = None)
@option('--batch-size', '-b', type = int, default = MAX_BATCH_SIZE)
def collect(community: str, count: int, batch_size: int):
    print(community)

    vk = VkApi(api_key = env.get('COLD_VK_API_KEY'))

    with open('assets/some-posts.json', encoding = 'utf-8', mode = 'w') as file:
        dump({'posts': vk.get_posts(community, count = count, batch_size = batch_size)}, file, indent = 2, ensure_ascii = False)


if __name__ == '__main__':
    main()
