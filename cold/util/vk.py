from functools import wraps
from tqdm import tqdm
from requests import post
from time import sleep

from ..PostsCorpus import Attachment, AttachmentType
from .captcha import try_raise_captcha_error, try_add_captcha_params, handle_captcha, get_key_from_external_service, get_key_using_model

MAX_BATCH_SIZE = 100
VERSION = '5.131'

TOO_MANY_VOTINGS_ERROR_CODE = 250

TOO_MANY_REQUESTS_PER_SECOND_ERROR_CODE = 6
FLOOD_CONTROL_ERROR_CODE = 9

MIN_REQUEST_TIME_INTERVAL = 1 / 3  # at max there may be 3 requests per second
MAX_REQUEST_TIME_INTERVAL = 1
TIME_INTERVAL_MULTIPLIER = 2


class TooManyRequestsException(Exception):
    pass


class FloodControlException(Exception):
    pass


def handle_too_many_requests_per_second(send_request):
    @wraps(send_request)
    def handle_too_many_requests_per_second_(*args, **kwargs):
        sleep_interval = MIN_REQUEST_TIME_INTERVAL

        while True:
            try:
                return send_request(*args, **kwargs)
            except (TooManyRequestsException, FloodControlException):
                sleep(sleep_interval)

            if sleep_interval < MAX_REQUEST_TIME_INTERVAL:
                sleep_interval *= TIME_INTERVAL_MULTIPLIER

    return handle_too_many_requests_per_second_


class VkApi:
    def __init__(self, api_key: str, timeout: int = 60):
        self.api_key = api_key
        self.timeout = timeout

    @handle_captcha(get_key = get_key_using_model)
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

    @handle_captcha(get_key = get_key_using_model)
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

    @handle_too_many_requests_per_second
    @handle_captcha(get_key = get_key_using_model)
    def add_vote(self, poll: Attachment, answers: tuple[str], captcha_sid: int = None, captcha_key: str = None):
        global TOO_MANY_REQUESTS_PER_SECOND_ERROR_CODE, TOO_MANY_VOTINGS_ERROR_CODE
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

                    if (error := body.get('error')) is not None:
                        if (code := error.get('error_code')) == TOO_MANY_REQUESTS_PER_SECOND_ERROR_CODE:
                            raise TooManyRequestsException('There are too many requests per second')
                        elif code == FLOOD_CONTROL_ERROR_CODE:
                            raise FloodControlException('Flood control')
                        elif code == TOO_MANY_VOTINGS_ERROR_CODE:
                            return body

                    raise ValueError(f'Inacceptable response body: {body}')

                return code == 1
            case value:
                raise ValueError(f'Inacceptable response status: {value}')
