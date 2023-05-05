from __future__ import annotations

from enum import Enum
from json import load

from .VotersFrequency import VotersFrequency


class AttachmentType(Enum):
    PHOTO = 'photo'
    VIDEO = 'video'
    POLL = 'poll'
    AUDIO = 'audio'
    LINK = 'link'
    DOC = 'doc'
    ALBUM = 'album'


class VotersAnswer:
    def __init__(self, ids: tuple[int], answer: str, rate: float):
        self.ids = ids
        self.answer = answer
        self.rate = rate


class Answer:
    def __init__(self, content: dict):
        self.content = content

    @property
    def id(self):
        return self.content['id']

    @property
    def text(self):
        return self.content['text']

    @property
    def rate(self):
        return self.content['rate']


class Attachment:
    def __init__(self, content: dict):
        self.content = content
        self.type = type_ = AttachmentType(content['type'])

        if type_ == AttachmentType.POLL:
            self.answers = tuple(Answer(content = answer) for answer in content['poll']['answers'])
            self.voters = None

    @property
    def id(self):
        match self.type:
            case AttachmentType.POLL:
                return self.content['poll']['id']
            case _:
                raise ValueError(f'Cannot obtain id for attachment of type {self.type}')

    @property
    def author_id(self):
        match self.type:
            case AttachmentType.POLL:
                return self.content['poll']['author_id']
            case _:
                raise ValueError(f'Cannot obtain author id for attachment of type {self.type}')

    def add_voters(self, response: dict, frequency: VotersFrequency, name: str):
        voters = []

        if (content := response.get('response')) is None:
            raise ValueError(f'Incorrect response: {response}')

        for answer in content:
            answer_id = answer['answer_id']
            for reference_answer in self.answers:
                if reference_answer.id == answer_id:
                    frequency.extend(users := answer['users']['items'], reference_answer.text, name)
                    voters.append(VotersAnswer(users, answer = reference_answer.text, rate = reference_answer.rate))
                    break
            else:
                raise ValueError(f'Cannot decode answer id {answer_id}')

        self.voters = voters

    def get_answer_id(self, texts: tuple[str]):
        match self.type:
            case AttachmentType.POLL:
                available_answers = []
                first_text = True
                for text in texts:
                    for answer in self.answers:
                        if answer.text == text:
                            return answer.id
                        elif first_text:
                            available_answers.append(answer.text)
                    first_text = False

                raise ValueError(f'Cannot obtain an id for provided text "{text}"; available values are {", ".join(available_answers)}')
            case _:
                raise ValueError('Cannot get answer id for non-pull attachment')


class Post:
    def __init__(self, content: dict):
        self.content = content
        self.attachments = tuple(Attachment(content = attachment) for attachment in content['attachments'])

    @property
    def polls(self):
        return tuple(attachment for attachment in self.attachments if attachment.type == AttachmentType.POLL)

    @property
    def text(self):
        return self.content['text']


class PostsCorpusIterator:
    def __init__(self, corpus: PostsCorpus):
        self.corpus = corpus

        self._index = 0
        self._n_posts = len(corpus.posts)

    def __next__(self):
        if self._index < self._n_posts:
            try:
                return self.corpus.posts[self._index]
            finally:
                self._index += 1
        raise StopIteration

    def __iter__(self):
        return self


class PostsCorpus:
    def __init__(self, path: str = None, content: dict = None):
        assert path is None and content is not None or path is not None and content is None

        if content is None:
            with open(path, encoding = 'utf-8', mode = 'r') as file:
                self.content = content = load(file)
                self.posts = tuple(Post(content = post) for post in content['posts'])
        else:
            self.content = content
            self.posts = tuple(Post(content = post) for post in content['posts'])

    def __iter__(self):
        return PostsCorpusIterator(corpus = self)

    @property
    def length(self):
        return len(self.posts)
