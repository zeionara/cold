from json import JSONEncoder as JSONEncoderBase


class JSONEncoder(JSONEncoderBase):
    def default(self, o):
        return o.as_dict
