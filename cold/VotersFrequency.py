from pandas import DataFrame, read_csv, concat

TAB = '\t'


class VotersFrequency:
    def __init__(self, path: str = None):
        # self.content = {}
        self.path = path
        if path is not None:
            self.cache = cache = read_csv(path, sep = TAB)
            self.polls = set(cache.poll.unique())
        self.rows = []

    def extend(self, users: tuple[int], answer: str, name: str):
        for user in users:
            self.rows.append((user, answer, name))

        if self.path is not None:
            self.polls.add(name)

        # for user_id in users:
        #     if (frequency := self.content.get(user_id)) is None:
        #         self.content[user_id] = 1
        #     else:
        #         self.content[user_id] = frequency + 1

    def is_cached(self, poll: str):
        if self.path is None:
            return False
        return poll in self.polls
        # print(self.cache)
        # raise NotImplementedError('Cache usage is not implemented yet')

    @property
    def df(self):
        df = DataFrame(self.rows, columns = ('user', 'answer', 'poll'))

        if self.path is None:
            return df

        return concat([self.cache, df])
