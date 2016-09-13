import json

from tornado.httpclient import HTTPResponse
from tornado.ioloop import IOLoop
from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.web import Application, RequestHandler, asynchronous
from tornado.gen import sleep, coroutine
from app.handlers.common import as_json


class GetOK(RequestHandler):
    @as_json
    def get(self, *args, **kwargs):
        return {"success": True}

    @staticmethod
    def validate(resp):
        assert isinstance(resp, HTTPResponse)
        assert resp.headers.get("Content-Type").startswith("application/json")
        assert json.dumps({"success": True}) == resp.body.decode('utf-8')


class GetAssertStatus(RequestHandler):
    @as_json
    def get(self, *args, **kwargs):
        assert False, ("fail", 500)

    @staticmethod
    def validate(resp):
        assert isinstance(resp, HTTPResponse)
        assert resp.code == 500
        ret = json.loads(resp.body.decode())
        assert ret['error'] == "fail"

class GetAssertString(RequestHandler):
    @as_json
    def get(self, *args, **kwargs):
        assert False, "fail"

    @staticmethod
    def validate(resp):
        assert isinstance(resp, HTTPResponse)
        assert resp.code == 200
        ret = json.loads(resp.body.decode())
        assert ret['error'] == "fail"


class GetAssertTuple(RequestHandler):
    @as_json
    def get(self, *args, **kwargs):
        assert False, ("fail", "message")

    @staticmethod
    def validate(resp):
        ret = json.loads(resp.body.decode())
        assert ret['error'] == "fail"
        assert ret['message'] == 'message'


class GetAssertExtraString(RequestHandler):
    @as_json
    def get(self, *args, **kwargs):
        assert False, ("fail", "message", "extra")

    @staticmethod
    def validate(resp):
        ret = json.loads(resp.body.decode())
        assert ret['error'] == "fail"
        assert ret['message'] == 'message'
        assert set(ret.keys()) == {"error", "message"}


class GetAssertExtraDict(RequestHandler):
    @as_json
    def get(self, *args, **kwargs):
        assert False, ("fail", "message", {'focus': "name"})

    @staticmethod
    def validate(resp):
        ret = json.loads(resp.body.decode())
        assert ret['error'] == "fail"
        assert ret['message'] == 'message'
        assert ret['focus'] == 'name'


class GetError(RequestHandler):
    @as_json
    def get(self, *args, **kwargs):
        raise Exception("oh")

    @staticmethod
    def validate(resp:HTTPResponse):
        assert resp.code == 500
        assert not resp.headers.get("Content-Type").startswith("application/json")


class AsyncGetOK(RequestHandler):
    @as_json
    @asynchronous
    def get(self, *args, **kwargs):
        return {"success": True}

    @staticmethod
    def validate(resp:HTTPResponse):
        ret = json.loads(resp.body.decode())
        assert ret['success'] == True


class AsyncGetOKCallback(RequestHandler):
    @as_json
    @asynchronous
    def get(self, *args, **kwargs):
        IOLoop.current().add_callback(self.on_callback)

    @as_json
    def on_callback(self):
        return {"success": True}

    @staticmethod
    def validate(resp:HTTPResponse):
        ret = json.loads(resp.body.decode())
        assert ret['success'] == True


class AsyncGetAssert(RequestHandler):
    @as_json
    @asynchronous
    def get(self, *args, **kwargs):
        assert False, "fail"

    @staticmethod
    def validate(resp:HTTPResponse):
        ret = json.loads(resp.body.decode())
        assert ret['error'] == "fail"


class AsyncGetAssertCallback(RequestHandler):
    @as_json
    @asynchronous
    def get(self, *args, **kwargs):
        IOLoop.current().add_callback(self.on_callback)

    @as_json
    def on_callback(self):
        assert False, "fail"

    @staticmethod
    def validate(resp:HTTPResponse):
        ret = json.loads(resp.body.decode())
        assert ret['error'] == "fail"


class AsyncGetError(RequestHandler):
    @as_json
    @asynchronous
    def get(self, *args, **kwargs):
        raise Exception('oh')

    @staticmethod
    def validate(resp:HTTPResponse):
        assert resp.code == 500
        assert not resp.headers.get("Content-Type").startswith("application/json")


class Async2GetOK(RequestHandler):
    @asynchronous
    @as_json
    def get(self, *args, **kwargs):
        return {"success": True}

    @staticmethod
    def validate(resp:HTTPResponse):
        ret = json.loads(resp.body.decode())
        assert ret['success'] == True


class Async2GetOKCallback(RequestHandler):
    @asynchronous
    @as_json
    def get(self, *args, **kwargs):
        IOLoop.current().add_callback(self.on_callback)

    @as_json
    def on_callback(self):
        return {"success": True}

    @staticmethod
    def validate(resp:HTTPResponse):
        ret = json.loads(resp.body.decode())
        assert ret['success'] == True


class Async2GetAssert(RequestHandler):
    @asynchronous
    @as_json
    def get(self, *args, **kwargs):
        assert False, "fail"

    @staticmethod
    def validate(resp:HTTPResponse):
        ret = json.loads(resp.body.decode())
        assert ret['error'] == "fail"


class Async2GetAssertCallback(RequestHandler):
    @asynchronous
    @as_json
    def get(self, *args, **kwargs):
        IOLoop.current().add_callback(self.on_callback)

    @as_json
    def on_callback(self):
        assert False, "fail"

    @staticmethod
    def validate(resp:HTTPResponse):
        ret = json.loads(resp.body.decode())
        assert ret['error'] == "fail"


class CoroutineGetOK(RequestHandler):
    @as_json
    @coroutine
    def get(self, *args, **kwargs):
        yield sleep(0.5)
        return {"success": True}

    @staticmethod
    def validate(resp:HTTPResponse):
        ret = json.loads(resp.body.decode())
        assert ret['success']


class CoroutineGetAssert(RequestHandler):
    @as_json
    @coroutine
    def get(self, *args, **kwargs):
        yield sleep(0.5)
        assert False, 'fail'

    @staticmethod
    def validate(resp:HTTPResponse):
        ret = json.loads(resp.body.decode())
        assert ret['error'] == "fail"


############################################################
class RespondJsonDecoratorTest(AsyncHTTPTestCase):
    def get_app(self):
        li = [
            GetOK,
            GetAssertString,
            GetAssertStatus,
            GetAssertTuple,
            GetAssertExtraString,
            GetAssertExtraDict,
            GetError,
            AsyncGetOK,
            AsyncGetOKCallback,
            AsyncGetAssert,
            AsyncGetAssertCallback,
            AsyncGetError,
            Async2GetOK,
            Async2GetOKCallback,
            Async2GetAssert,
            Async2GetAssertCallback,
            CoroutineGetOK,
            CoroutineGetAssert,
        ]
        routes = []
        for i, klass in enumerate(li):
            routes.append((
                "/{}".format(i),
                klass,
            ))
        return Application(routes)

    @gen_test
    def test_all(self):
        for spec in self.get_app().handlers[0][1]:
            print(spec.handler_class.__name__, end=", ")
            resp = yield self.http_client.fetch(self.get_url(spec._path), raise_error=False)
            spec.handler_class.validate(resp)
            print("ok")

