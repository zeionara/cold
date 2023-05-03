from json import dump, dumps, load
from click import group, argument, option

from .util import Spec, JSONEncoder, VkApi, MAX_BATCH_SIZE
from .PostsCorpus import PostsCorpus
from .VotersFrequency import VotersFrequency

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
@option('--path', '-p', type = str, default = 'assets/some-posts.json')
def collect(community: str, count: int, batch_size: int, path: str):
    print(community)

    vk = VkApi(api_key = env.get('COLD_VK_API_KEY'))
    posts = {'posts': vk.get_posts(community, count = count, batch_size = batch_size)}

    # with open(path, encoding = 'utf-8', mode = 'w') as file:
    #     dump({'posts': vk.get_posts(community, count = count, batch_size = batch_size)}, file, indent = 2, ensure_ascii = False)

    frequency = VotersFrequency()

    for post in PostsCorpus(content = posts):
        polls = post.polls

        if len(polls) > 0:
            first_poll = polls[0]

            try:
                first_poll.add_voters(vk.get_voters(first_poll), frequency, name = post.text.split('\n')[0].replace('на #lm', '').strip())
            except ValueError:
                pass

    print(frequency.df)


@main.command()
@argument('path', type = str, default = 'assets/some-posts.json')
def process(path: str):
    vk = VkApi(api_key = env.get('COLD_VK_API_KEY'))
    frequency = VotersFrequency()

    for post in PostsCorpus(path = path):
        polls = post.polls

        if len(polls) > 0:
            first_poll = polls[0]

            print(first_poll.id)
            print(first_poll.get_answer_id('Не смотрел(-а)'))

            try:
                first_poll.add_voters(vk.get_voters(first_poll), frequency, name = post.text.split('\n')[0])
            except ValueError:
                pass

            return

    print(frequency.df)


if __name__ == '__main__':
    main()
