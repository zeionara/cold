from tqdm import tqdm
from requests import post

from ..PostsCorpus import Attachment, AttachmentType

MAX_BATCH_SIZE = 100


class VkApi:
    def __init__(self, api_key: str, timeout: int = 60):
        self.api_key = api_key
        self.timeout = timeout

    def get_posts_(self, domain: str, count: int, offset: int) -> dict:
        response = post(
            'https://api.vk.com/method/wall.get', data = {
                'access_token': self.api_key,
                'domain': domain,
                'count': count,
                'offset': offset,
                'filter': 'owner',
                'v': '5.131'
            },
            timeout = self.timeout
        )

        match response.status_code:
            case 200:
                return response.json()
            case value:
                raise ValueError(f'Inacceptable response status: {value}')

    def get_posts(self, domain: str, count: int = None, batch_size: int = MAX_BATCH_SIZE):
        offset = 0

        all_items = []
        n_items = batch_size

        pbar = None

        if count is not None:
            pbar = tqdm(total = count)

        # with tqdm(total = count) as pbar:
        while (count is None or offset < count) and n_items == batch_size:

            response = self.get_posts_(domain, count = batch_size, offset = offset)

            items = response['response']['items']

            all_items.extend(items)
            n_items = len(items)
            offset += n_items

            if pbar is None:
                pbar = tqdm(total = (count := response['response']['count']))

            pbar.update(n_items)

        return all_items

    def get_voters(self, poll: Attachment):
        assert poll.type == AttachmentType.POLL, 'Cannot get voters for non-poll attachment'

        response = post(
            'https://api.vk.com/method/polls.getVoters', data = {
                'access_token': self.api_key,
                'poll_id': poll.id,
                'answer_ids': ','.join(str(answer.id) for answer in poll.answers),
                'v': '5.131'
            },
            timeout = self.timeout
        )

        match response.status_code:
            case 200:
                return response.json()
            case value:
                raise ValueError(f'Inacceptable response status: {value}')
