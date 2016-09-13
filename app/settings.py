# coding:utf-8
import os

# 项目名字，默认用模块目录，请自己改掉
PROJECT = 'wherego'

# 用来加解密cookie的秘钥
COOKIE_SECRET = 'define your cookie secret to encrypt/decrypt cookie'
LOGIN_URL = "/login"

# mongo服务器名，不配置就使用None（即本机）
MONGODB_HOST = os.getenv("mongodb_host")
DB_NAME = PROJECT

# DEBUG开关
# 打开以后，tornado会在页面输出具体的出错信息；production环境下需关闭
# 如果存在xxx_debug的环境变量，就按照环境变量来定义是否处于DEBUG状态
DEBUG = __debug__ or bool(os.getenv("debug".format(PROJECT)))

# 日志级别
LOG_LEVEL = "DEBUG"
if not DEBUG:
    LOG_LEVEL = os.getenv("log", "INFO").upper()

# 各种目录
FOLDER_PACKAGE = os.path.dirname(__file__)
FOLDER_TEMPLATE = os.path.join(FOLDER_PACKAGE, 'templates')
FOLDER_STATIC = os.path.join(FOLDER_PACKAGE, 'static')


# 打印全局变量，供检查 ===============================================
for key, val in sorted(list(locals().items()), key=lambda x: x[0]):
    if key == key.upper() and key not in ['COOKIE_SECRET']:
        print("{:<25}: {}".format(key, val))


