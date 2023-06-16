# from random import random

from time import sleep
from json import dump, dumps

from click import group, argument, option
from tqdm import tqdm

import vk_captchasolver as vc

from .util import Spec, JSONEncoder, VkApi, MAX_BATCH_SIZE, MIN_REQUEST_TIME_INTERVAL, Captcha
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
@argument('sid', type = int, required = False)
@option('-p', '--path', type = str)
@option('-u', '--url', type = str)
@option('-s', type = int, default = 1)
def solve(sid: int, s: int, url: str, path: str):
    if url is None:
        print(vc.solve(sid = sid, s = s) if path is None else Captcha(path = path).text)
    else:
        print(Captcha(url = url).text)


@main.command()
@argument('path', type = str, default = 'assets/some-posts.json')
@option('--delay', '-d', type = float, default = MIN_REQUEST_TIME_INTERVAL)
@option('--output', '-o', type = str, default = 'assets/some-posts.tsv')
@option('--verbose', '-v', is_flag = True)
@option('--checkpoint-frequency', '-cf', type = int, default = 1000)
def process(path: str, delay: float, output: str, verbose: bool, checkpoint_frequency: int):
    vk = VkApi(api_key = env.get('COLD_VK_API_KEY'))
    frequency = VotersFrequency()

    corpus = PostsCorpus(path = path)
    # print(corpus.length)
    pbar = tqdm(total = corpus.length)

    current_voter_id = int(env.get('COLD_USER_ID'))

    def checkpoint(verbose: bool = False):
        df = frequency.df
        df_transformed = df[df['user'] != current_voter_id].reset_index(drop = True)

        if verbose:
            print(df_transformed)

        df_transformed.to_csv(output, sep = '\t')

    for (i, post) in enumerate(corpus, start = 1):
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
                else:
                    print(f'Unexpected error, skipping poll {name} (id = {first_poll.id}), body = {vote_accepted}')

            # return

            # sleep(delay)
            # sleep(0.3 + random() * delay)

            sleep(MIN_REQUEST_TIME_INTERVAL)
            try:
                first_poll.add_voters(vk.get_voters(first_poll), frequency, name = name)
            except ValueError as e:
                if verbose:
                    print(e)

            # sleep(delay)
            # sleep(0.3 + random() * delay)

        pbar.update(1)

        if i % checkpoint_frequency == 0:
            checkpoint(verbose = False)

    checkpoint(verbose = verbose)


if __name__ == '__main__':
    main()
