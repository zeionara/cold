CAPTCHA_ERROR_CODE = 14


class CaptchaNeeded(Exception):
    def __init__(self, sid: str, image: str):
        super().__init__(f'Captca needed (see {image}, send answer to {sid})')

        self.sid = sid
        self.image = image


def handle_captcha(send_request):
    def handle_captcha_(*args, **kwargs):
        while True:
            try:
                return send_request(*args, **kwargs)
            except CaptchaNeeded as error:
                key = input(f'Captcha needed: {error.image}\n')

                kwargs['captcha_sid'] = error.sid
                kwargs['captcha_key'] = key

                return handle_captcha_(*args, **kwargs)

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
