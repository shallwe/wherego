# coding:utf-8
from tornado import web, template
from jinja2 import Environment, FileSystemLoader

from app.settings import *
from app.handlers import index

env = Environment(
    loader=FileSystemLoader(FOLDER_TEMPLATE),
    extensions=[
        'pyjade.ext.jinja.PyJadeExtension',
        "jinja2.ext.with_",
    ],
    # 如果和angular的{{ }}符号冲突，那么可以在下面自定义
    # variable_start_string="{=",
    # variable_end_string="=}"
)


class Jinja2TemplateLoader(template.Loader):
    def _create_template(self, name):
        t = env.get_template(name)
        # 生成模板时，tornado会调用generate方法，但是在jinja2里面generate会生成一个generator（而不是string）
        t.generate = t.render
        return t


# 所有的url映射定义在这一处
routes = [
    ('/', index.IndexPage),
    ('/chart', index.ChartPage),
    ]


application = web.Application(
    routes,
    login_url=LOGIN_URL,
    template_loader=Jinja2TemplateLoader(FOLDER_TEMPLATE),
    static_path=FOLDER_STATIC,
    cookie_secret=COOKIE_SECRET,
    debug=DEBUG,
    autoreload=False,
)

# application.sentry_client = AsyncSentryClient(SENTRY_DSN)
