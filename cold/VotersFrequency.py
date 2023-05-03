from pandas import DataFrame


class VotersFrequency:
    def __init__(self):
        # self.content = {}
        self.rows = []

    def extend(self, users: tuple[int], answer: str, name: str):
        for user in users:
            self.rows.append((user, answer, name))

        # for user_id in users:
        #     if (frequency := self.content.get(user_id)) is None:
        #         self.content[user_id] = 1
        #     else:
        #         self.content[user_id] = frequency + 1

    @property
    def df(self):
        return DataFrame(self.rows, columns = ('user', 'answer', 'poll'))
