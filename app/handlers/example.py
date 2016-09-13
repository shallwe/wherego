# coding:utf-8
import logging

from app.handlers.base import BaseRequestHandler
from app.handlers.common import as_json
from app.settings import PROJECT
from voluptuous import Schema

log = logging.getLogger("index")


class SimplePage(BaseRequestHandler):
    def get(self):
        self.render("example.jade",
                    project=PROJECT)


class UrlParams(BaseRequestHandler):
    def get(self, a, b, c, d, e):
        m = [
            "a={}".format(a),
            "b={}".format(b),
            "c={}".format(c),
            "d={}".format(d),
            "e={}".format(e),
        ]
        self.write("<br>".join(m))


class Initialize(BaseRequestHandler):
    def initialize(self, key):
        self.key = key

    def get(self, a, b, c, d, e):
        self.write("initialize param 'key' is {}".format(self.key))


class ReverseUrl(BaseRequestHandler):
    def get(self, a):
        self.write("""reverse_url('example', '{}') == {}""".format(a, self.reverse_url('example_name', a)))


class JsonPost(BaseRequestHandler):
    @as_json
    def post(self):
        data = self.read_json(Schema({
            "i": int,
        }))
        return data
