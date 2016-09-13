# coding:utf-8
import json
from app.handlers.common.errors import InvalidBody, InvalidJson

from tornado.web import RequestHandler
from voluptuous import Schema


class BaseRequestHandler(RequestHandler):
    def read_json(self, schema: Schema=None) -> dict:
        """读取body中的json，并且进行格式验证"""
        try:
            body = self.request.body.decode()
        except:
            raise InvalidBody
        try:
            data = json.loads(body)
        except:
            raise InvalidJson
        if schema:
            data = schema(data)
        return data


class Page(BaseRequestHandler):
    def initialize(self, name): # name 由 routes 中的 dict 传入
        self.name = name

    def get(self, *args, **kwargs):
        self.render(self.name,
                    args=args,
                    **kwargs)
