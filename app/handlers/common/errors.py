# coding:utf-8
"""
在这里统一存放错误码和Exception
"""
INVALID_BODY = "INVALID_BODY"
INVALID_JSON = "INVALID_JSON"
INVALID_DATA = "INVALID_DATA"
REQUIRED = 'required'
INVALID = 'invalid'


class ResponableException(Exception):
    def __init__(self):
        self.error = None
        self.extra = None
        self.status = 200

    def to_dict(self):
        ret = {}
        if self.error:
            ret['error'] = self.error
        if isinstance(self.extra, dict):
            ret.update(self.extra)
        return ret


class InvalidBody(ResponableException):
    def __init__(self):
        super(InvalidBody, self).__init__()
        self.error = INVALID_BODY


class InvalidJson(ResponableException):
    def __init__(self):
        super(InvalidJson, self).__init__()
        self.error = INVALID_JSON
