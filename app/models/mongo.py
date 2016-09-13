# coding:utf-8
"""
http://docs.mongoengine.org/en/latest/index.html
"""
from mongoengine import *

from app.handlers.common import jsonable
from app.settings import MONGODB_HOST, DB_NAME

db = connect(DB_NAME, host=MONGODB_HOST)


def to_json(self, *args, **kwargs):
    data = self.to_mongo()
    data['id'] = data['_id']
    data.pop('_id')
    return jsonable(data)

Document.to_json = to_json


# class User(Document):
#     account = StringField(required=True)
#     password_hash = StringField()
#     create_time = DateTimeField()
