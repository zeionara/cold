from re import compile as re_compile

from vk_captchasolver import solve


class Captcha:
    url_pattern = re_compile('sid=([0-9]+)&s=([0-9]+)')

    def __init__(self, *, url: str = None, path: str = None):
        assert url is None and path is not None or url is not None and path is None, 'Either path either url must not be none, but not both of these parameters'

        if url is not None:
            matches = Captcha.url_pattern.findall(url)

            if len(matches) < 1:
                raise ValueError(f'Cannot parse captcha url: {url}')

            first_match = matches[0]

            self.sid = int(first_match[0])
            self.s = int(first_match[1])

        self.path = path
        self.url = url

    @property
    def text(self):
        if self.url is None:
            return solve(image = self.path)
        return solve(sid = self.sid, s = self.s)
