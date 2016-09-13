# coding:utf-8
import logging

from app.handlers.base import BaseRequestHandler
from app.handlers.common import as_json

log = logging.getLogger("index")


class IndexPage(BaseRequestHandler):
    def get(self):
        self.render("index.jade")

