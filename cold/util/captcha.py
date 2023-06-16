from functools import wraps
from webbrowser import get as browser

from .Captcha import Captcha


CAPTCHA_ERROR_CODE = 14

chrome = browser('google-chrome')

N_MAX_MODEL_ATTEMPTS = 10
current_attempt = 0


class CaptchaNeeded(Exception):
    def __init__(self, sid: str, image: str):
        super().__init__(f'Captca needed (see {image}, send answer to {sid})')

        self.sid = sid
        self.image = image


def type_key(url: str):
    chrome.open_new_tab(url)
    return input(f'Captcha needed: {url}\n')


def get_key_using_model(url: str):
    global current_attempt

    if current_attempt > N_MAX_MODEL_ATTEMPTS:
        return type_key(url)

    print(f'Trying to solve captcha automatically {current_attempt}...')
    current_attempt += 1

    return Captcha(url = url).text
    # raise NotImplementedError(f'Cannot solve captcha using model: {url}')


def get_key_from_external_service(url: str):
    raise NotImplementedError(f'External service for captcha decoding is not configured: {url}')


def handle_captcha(get_key: callable = type_key):
    def handle_captcha_(send_request):
        @wraps(send_request)
        def handle_captcha__(*args, **kwargs):
            global current_attempt

            while True:
                try:
                    result = send_request(*args, **kwargs)
                    current_attempt = 0
                    return result
                except CaptchaNeeded as error:
                    kwargs['captcha_sid'] = error.sid
                    kwargs['captcha_key'] = get_key(error.image)

                    return handle_captcha__(*args, **kwargs)

        return handle_captcha__

    return handle_captcha_


def try_raise_captcha_error(response: dict):
    error = response.get('error')

    if error is not None and error.get('error_code') == CAPTCHA_ERROR_CODE:
        raise CaptchaNeeded(sid = int(error['captcha_sid']), image = error['captcha_img'])


def try_add_captcha_params(request: dict, captcha_sid: int = None, captcha_key: str = None):
    if captcha_sid is not None and captcha_key is not None:
        request['captcha_sid'] = captcha_sid
        request['captcha_key'] = captcha_key

    return request
