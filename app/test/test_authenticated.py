import json

from tornado.httpclient import HTTPResponse
from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.web import RequestHandler, Application
from app.handlers.common import authenticated


class Default(RequestHandler):
    @authenticated
    def get(self, *args, **kwargs):
        return 'ok'

    @staticmethod
    def validate(resp:HTTPResponse):
        assert resp.code == 302
        assert resp.headers.get("location").startswith("/login")

class Json(RequestHandler):
    @authenticated("json")
    def get(self, *args, **kwargs):
        return 'ok'

    @staticmethod
    def validate(resp:HTTPResponse):
        assert resp.code == 403
        ret = json.loads(resp.body.decode())
        assert ret['error'] == "UNAUTHORIZED"


class Status(RequestHandler):
    @staticmethod
    def setup(app):
        app.settings['unauthorized_json_status'] = 200

    @staticmethod
    def cleanup(app):
        app.settings.pop('unauthorized_json_status')

    @authenticated("json")
    def get(self, *args, **kwargs):
        return 'ok'

    @staticmethod
    def validate(resp:HTTPResponse):
        assert resp.code == 200
        ret = json.loads(resp.body.decode())
        assert ret['error'] == "UNAUTHORIZED"


class Error(RequestHandler):
    @staticmethod
    def setup(app):
        app.settings['unauthorized_json_error'] = "Hello"

    @staticmethod
    def cleanup(app):
        app.settings.pop('unauthorized_json_error')

    @authenticated("json")
    def get(self, *args, **kwargs):
        return 'ok'

    @staticmethod
    def validate(resp:HTTPResponse):
        assert resp.code == 403
        ret = json.loads(resp.body.decode())
        assert ret['error'] == "Hello"



############################################################
class AuthenticatedDecoratorTest(AsyncHTTPTestCase):
    def get_app(self):
        li = [
            Default,
            Json,
            Status,
            Error,
        ]
        routes = []
        for i, klass in enumerate(li):
            routes.append((
                "/{}".format(i),
                klass,
            ))
        return Application(routes, debug=True, login_url="/login")

    @gen_test
    def test_all(self):
        for spec in self.get_app().handlers[0][1]:
            print(spec.handler_class.__name__, end=", ")
            if hasattr(spec.handler_class, "setup"):
                spec.handler_class.setup(self._app)
            resp = yield self.http_client.fetch(self.get_url(spec._path), raise_error=False, follow_redirects=False)
            spec.handler_class.validate(resp)
            if hasattr(spec.handler_class, "cleanup"):
                spec.handler_class.cleanup(self._app)
            print("ok")

        # header带accept:json，就会自动返回json，不走html路线
        resp = yield self.http_client.fetch(self.get_url("/0"), headers={"accept": "application/json"}, raise_error=False, follow_redirects=False)
        ret = json.loads(resp.body.decode())
        assert ret['error'] == "UNAUTHORIZED"