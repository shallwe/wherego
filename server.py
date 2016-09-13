# coding:utf-8
import logging
import os

from tornado import ioloop, httpserver
from tornado.options import options, define

from app import application
from app.settings import PROJECT, LOG_LEVEL


def main():
    log = logging.getLogger(PROJECT+'.server')
    options.logging = LOG_LEVEL

    define('port', default=8000, type=int, help='server port')
    define('key', default=None, help='ssl key path')
    define('cert', default=None, help='ssl crt path')

    options.parse_command_line()

    ssl_options = None
    if options.key and options.cert:
        assert os.path.exists(options.key), 'key file not exists: {}'.format(options.key)
        assert os.path.exists(options.cert), 'crt file not exists: {}'.format(options.cert)

        ssl_options = {'certfile': options.cert, 'keyfile': options.key}
        log.info('https mode')

    http_server = httpserver.HTTPServer(application,
                                        ssl_options=ssl_options,
                                        xheaders=True)

    # 默认tornado会把日志时间精确到秒，这里改成精确到毫秒
    log.root.handlers[0].formatter.datefmt = ''

    log.info('Serving on port: {}'.format(options.port))
    http_server.listen(options.port)
    log.debug('Ready!')

    ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()