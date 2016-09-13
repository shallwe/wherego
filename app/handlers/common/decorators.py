# coding:utf-8
from functools import wraps, partial
import urllib.parse as urlparse
from urllib.parse import urlencode

from tornado.concurrent import Future
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, HTTPError
from tornado.httputil import HTTPServerRequest
from voluptuous import MultipleInvalid, RequiredFieldInvalid, Invalid
from app.handlers.common.errors import ResponableException, INVALID_DATA, REQUIRED, INVALID
from app.handlers.common.parse import jsonable


def _error_to_resp(e:Exception) -> (dict, int):
    """
    将Exception转化为dict，用来给as_json返回数据
    可以根据自己的需要扩展和改写
    """
    if isinstance(e, ResponableException):
        return e.to_dict(), e.status
    elif isinstance(e, MultipleInvalid):
        ret = {
            "error": INVALID_DATA,
            "details": {}
        }
        for err in e.errors:
            path = ".".join([str(x) for x in err.path])
            if isinstance(err, RequiredFieldInvalid):
                ret['details'][path] = REQUIRED
            elif isinstance(err, Invalid):
                ret['details'][path] = INVALID
            else:
                assert False
        return ret, 200
    elif isinstance(e, AssertionError):
        """
        支持用法:
        assert False, "Error"   # -> {error:Error}
        Assert False, ("Error", "Message")  # -> {error:Error, message:Message}
        Assert False, ("Error", "Message", 500)  # -> {error:Error, message:Message}, status:500, status code 位置随意
        Assert False, ("Error", "Message", extraDict)  # -> {error:Error, message:Message}.update(extraDict)
        Assert False, dict  # -> dict
        """
        args = e.args[0]
        ret = {}
        status = 200

        if isinstance(args, str):
            ret["error"] = args
        elif isinstance(args, dict):
            ret.update(args)
        elif isinstance(args, tuple):
            for arg in args:
                if isinstance(arg, str):
                    if not ret.get("error"):
                        ret["error"] = arg
                    elif not ret.get('message'):
                        ret["message"] = arg
                elif isinstance(arg, dict):
                    ret.update(arg)
                elif isinstance(arg, int):
                    status = arg
        assert ret, "resp data is empty"
        return ret, status
    else:
        raise e


def as_json(method):
    """
    decorator for RequestHandler.get/post/...()
    将return值和Exception转化为json写回response

    用法：
    @as_json
    @其他decorator
    def get(self):...
    """

    @wraps(method)
    def decorated_handle_func(self: RequestHandler, *args, **kwargs):
        assert isinstance(self, RequestHandler)

        def render_error(e):
            if self._finished:
                return

            data, status = _error_to_resp(e)
            self.set_status(status)
            self.finish(data)

        # @respond_json+@asynchronous时需要, @asynchronous会截获exception
        def _stack_context_handle_exception(func, self, type_, value, traceback):
            if isinstance(value, Exception):
                render_error(value)
            else:
                return func(type_, value, traceback)

        self._stack_context_handle_exception = partial(_stack_context_handle_exception,
                                                       self._stack_context_handle_exception, self)

        try:
            ret = method(self, *args, **kwargs)

            if isinstance(ret, Future):
                def future_complete(f):
                    if not self._finished:
                        if f.exception():
                            render_error(f.exception())
                        else:
                            self.finish(jsonable(f.result()))

                self._auto_finish = False  # 防止future_complete之前就auto_finish了
                IOLoop.current().add_future(ret, future_complete)

            elif not self._auto_finish:
                return

            else:
                self.finish(jsonable(ret))

        except Exception as e:
            render_error(e)

    return decorated_handle_func


def authenticated(method_or_resp_type):
    """
    decorator for RequestHandler.method
    works like tornado's @authenticated,

    用法：
    @authenticated   // 自动推断返回类型，如果是accept:json，那么返回json错误信息(status:403)，如果是html，那么照常
    ...
    @authenticated("json")  // 强制返回json，status:403
    ...
    """

    def do_decorate(method, resp_type=None):
        @wraps(method)
        def decorated_method(self: RequestHandler, *args, **kwargs):
            if not self.current_user:
                req = self.request
                assert isinstance(req, HTTPServerRequest)

                if resp_type == "json" or "json" in req.headers.get("accept", ""):
                    error = self.settings.get("unauthorized_json_error", "UNAUTHORIZED")
                    status = self.settings.get("unauthorized_json_status", 403)
                    login_url = self.settings.get("login_url")

                    ret = {"error": error}
                    if login_url:
                        ret["loginURL"] = login_url
                    self.set_status(status)
                    return self.finish(ret)
                else:
                    # code from tornado
                    if self.request.method in ("GET", "HEAD"):
                        url = self.get_login_url()
                        if "?" not in url:
                            if urlparse.urlsplit(url).scheme:
                                # if login url is absolute, make next absolute too
                                next_url = self.request.full_url()
                            else:
                                next_url = self.request.uri
                            url += "?" + urlencode(dict(next=next_url))
                        self.redirect(url)
                        return
                    raise HTTPError(403)

            return method(self, *args, **kwargs)

        return decorated_method

    if callable(method_or_resp_type):
        return do_decorate(method_or_resp_type)
    else:
        return partial(do_decorate, resp_type=method_or_resp_type)
