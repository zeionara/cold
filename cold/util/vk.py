from tqdm import tqdm
from requests import post

from ..PostsCorpus import Attachment, AttachmentType
from .captcha import try_raise_captcha_error, try_add_captcha_params, handle_captcha

MAX_BATCH_SIZE = 100
VERSION = '5.131'

TOO_MANY_VOTINGS_ERROR_CODE = 250


class VkApi:
    def __init__(self, api_key: str, timeout: int = 60):
        self.api_key = api_key
        self.timeout = timeout

    @handle_captcha
    def get_posts_(self, domain: str, count: int, offset: int, captcha_sid: int = None, captcha_key: str = None) -> dict:
        response = post(
            'https://api.vk.com/method/wall.get', data = try_add_captcha_params({
                'access_token': self.api_key,
                'domain': domain,
                'count': count,
                'offset': offset,
                'filter': 'owner',
                'v': VERSION
            }, captcha_sid, captcha_key),
            timeout = self.timeout
        )

        match response.status_code:
            case 200:
                try_raise_captcha_error(body := response.json())

                return body
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

    @handle_captcha
    def get_voters(self, poll: Attachment, captcha_sid: int = None, captcha_key: str = None):
        assert poll.type == AttachmentType.POLL, 'Cannot get voters for non-poll attachment'

        response = post(
            'https://api.vk.com/method/polls.getVoters', data = try_add_captcha_params({
                'access_token': self.api_key,
                'poll_id': poll.id,
                'answer_ids': ','.join(str(answer.id) for answer in poll.answers),
                'v': VERSION
            }, captcha_sid, captcha_key),
            timeout = self.timeout
        )

        match response.status_code:
            case 200:
                try_raise_captcha_error(body := response.json())

                return body
            case value:
                raise ValueError(f'Inacceptable response status: {value}')

    @handle_captcha
    def add_vote(self, poll: Attachment, answers: tuple[str], captcha_sid: int = None, captcha_key: str = None):
        assert poll.type == AttachmentType.POLL, 'Cannot get voters for non-poll attachment'

        response = post(
            'https://api.vk.com/method/polls.addVote',
            data = try_add_captcha_params({
                'access_token': self.api_key,
                'poll_id': poll.id,
                'answer_ids': poll.get_answer_id(texts = answers),
                'v': VERSION
            }, captcha_sid, captcha_key),
            timeout = self.timeout
        )

        match response.status_code:
            case 200:
                code = (body := response.json()).get('response')

                if code is None:
                    try_raise_captcha_error(body)

                    if (error := body.get('error')) is not None and error.get('error_code') == TOO_MANY_VOTINGS_ERROR_CODE:
                        return None

                    raise ValueError(f'Inacceptable response body: {body}')

                return code == 1
            case value:
                raise ValueError(f'Inacceptable response status: {value}')
