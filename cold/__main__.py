# from random import random

from time import sleep
from json import dump, dumps

from click import group, argument, option
from tqdm import tqdm

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

    with open(path, encoding = 'utf-8', mode = 'w') as file:
        dump(posts, file, indent = 2, ensure_ascii = False)

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
@option('--delay', '-d', type = float, default = 1 / 3)  # at max there may be 3 requests per second
@option('--output', '-o', type = str, default = 'assets/some-posts.tsv')
@option('--verbose', '-v', is_flag = True)
def process(path: str, delay: float, output: str, verbose: bool):
    vk = VkApi(api_key = env.get('COLD_VK_API_KEY'))
    frequency = VotersFrequency()

    corpus = PostsCorpus(path = path)
    # print(corpus.length)
    pbar = tqdm(total = corpus.length)

    for post in corpus:
        polls = post.polls

        if len(polls) > 0:
            first_poll = polls[0]

            # print(first_poll.id)
            # print(first_poll.get_answer_id('Не смотрел(-а)'))

            name = post.text.split('\n')[0].replace('на #lm', '').strip().replace('"', "'")

            vote_accepted = vk.add_vote(first_poll, answers = ('Не смотрел(-а)', 'Результат', 'не смотрел(а)', 'Не смотрел(а)', 'Не сомтрел(а)', '+'))

            if verbose:
                if vote_accepted is True:
                    print(f'Vote accepted for {name}')
                elif vote_accepted is False:
                    print(f'Vote not accepted for {name}')
                elif vote_accepted is None:
                    print(f'Unexpected error, skipping poll {name} (id = {first_poll.id})')

            # return

            sleep(delay)
            # sleep(0.3 + random() * delay)

            try:
                first_poll.add_voters(vk.get_voters(first_poll), frequency, name = name)
            except ValueError:
                pass

            sleep(delay)
            # sleep(0.3 + random() * delay)

        pbar.update(1)

    df = frequency.df
    current_voter_id = int(env.get('COLD_USER_ID'))

    df_transformed = df[df['user'] != current_voter_id].reset_index(drop = True)

    if verbose:
        print(df_transformed)

    df_transformed.to_csv(output, sep = '\t')


if __name__ == '__main__':
    main()
