# coding:utf-8

from app.routes import _convert_rules
from tornado.gen import coroutine

from tornado.httpclient import HTTPResponse
from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.web import RequestHandler, Application


class IndexGet(RequestHandler):
    def get(self, *args, **kwargs):
        self.finish("index")

    @staticmethod
    def validate(resp: HTTPResponse):
        assert resp.body.decode() == "index"


class IndexGetOnly(RequestHandler):
    def get(self, *args, **kwargs):
        self.finish("ok")

    def post(self):
        self.finish("ok")

    @staticmethod
    def validate(resp: HTTPResponse):
        assert resp.error.code == 405


class OneParamNoFormat(RequestHandler):
    def get(self, x):
        return self.finish(x)

    @staticmethod
    @coroutine
    def test(t):
        resp = yield t.http_client.fetch(t.get_url("/param/a"), raise_error=False, follow_redirects=False)
        assert resp.body.decode() == "a"


class OneParamIntFormat(RequestHandler):
    def get(self, x):
        return self.finish(x)

    @staticmethod
    @coroutine
    def test(t):
        resp = yield t.http_client.fetch(t.get_url("/int/a"), raise_error=False, follow_redirects=False)
        assert resp.error.code == 404

        resp = yield t.http_client.fetch(t.get_url("/int/10"), raise_error=False, follow_redirects=False)
        assert resp.body.decode() == "10"


class OneParamHexFormat(RequestHandler):
    def get(self, x):
        return self.finish(x)

    @staticmethod
    @coroutine
    def test(t):
        resp = yield t.http_client.fetch(t.get_url("/hex/__"), raise_error=False, follow_redirects=False)
        assert resp.error.code == 404

        resp = yield t.http_client.fetch(t.get_url("/hex/10"), raise_error=False, follow_redirects=False)
        assert resp.body.decode() == "10"

        resp = yield t.http_client.fetch(t.get_url("/hex/10a"), raise_error=False, follow_redirects=False)
        assert resp.body.decode() == "10a"

        resp = yield t.http_client.fetch(t.get_url("/hex/10Ab"), raise_error=False, follow_redirects=False)
        assert resp.body.decode() == "10Ab"


class OneParamPathFormat(RequestHandler):
    def get(self, x):
        return self.finish(x)

    @staticmethod
    @coroutine
    def test(t):
        resp = yield t.http_client.fetch(t.get_url("/path/__"), raise_error=False, follow_redirects=False)
        assert resp.body.decode() == "__"

        resp = yield t.http_client.fetch(t.get_url("/path/10/lkjaf8u"), raise_error=False, follow_redirects=False)
        assert resp.body.decode() == "10/lkjaf8u"


class TwoParam(RequestHandler):
    def get(self, x, action):
        return self.finish(x + ':' + action)

    @staticmethod
    @coroutine
    def test(t):
        resp = yield t.http_client.fetch(t.get_url("/two/a/b"), raise_error=False, follow_redirects=False)
        assert resp.body.decode() == "a:b"


class Kwargs(RequestHandler):
    def initialize(self, key):
        self.key = key

    def get(self, x):
        return self.finish(self.key + ':' + x)

    @staticmethod
    @coroutine
    def test(t):
        resp = yield t.http_client.fetch(t.get_url("/kwargs/a"), raise_error=False, follow_redirects=False)
        assert resp.body.decode() == "hello:a"


class Named(RequestHandler):
    def get(self, x):
        return self.finish(x)

    @staticmethod
    @coroutine
    def test(t):
        assert t._app.reverse_url("the_name", "a") == "/named/a"


############################################################
class RoutesTest(AsyncHTTPTestCase):
    def get_app(self):
        rules = [
            ("/index", "GET", IndexGet),
            ("/index2", "POST", IndexGetOnly),
            ("/param/{x}", "GET", OneParamNoFormat),
            ("/int/{x:int}", "GET", OneParamIntFormat),
            ("/hex/{x:hex}", "GET", OneParamHexFormat),
            ("/path/{x:path}", "GET", OneParamPathFormat),
            ("/two/{x}/{action}", "GET", TwoParam),
            ("/kwargs/{x}", "GET", Kwargs, {"key": "hello"}),
            ("/named/{x}", "GET", Named, "the_name"),
        ]

        urls = _convert_rules(rules)
        return Application(urls, debug=True)

    @gen_test
    def test_all(self):
        for spec in self.get_app().handlers[0][1]:
            print(spec.handler_class.__name__, end=", ")
            if hasattr(spec.handler_class, "setup"):
                spec.handler_class.setup(self._app)

            if hasattr(spec.handler_class, "test"):
                yield spec.handler_class.test(self)
            else:
                resp = yield self.http_client.fetch(self.get_url(spec._path), raise_error=False, follow_redirects=False)
                spec.handler_class.validate(resp)
            if hasattr(spec.handler_class, "cleanup"):
                spec.handler_class.cleanup(self._app)
            print("ok")
