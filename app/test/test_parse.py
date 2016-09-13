# coding:utf-8
from datetime import datetime
import time
import bson
from app.handlers.common import jsonable, jsonable


def test_jsonable():
    o = {
        "hello": "world",
        "n": 1,
        "dt": datetime.now(),
        "_id": bson.ObjectId()
    }

    ret = jsonable(o)
    assert ret['hello'] == 'world'
    assert ret['n'] == 1
    assert type(ret['dt']) == float
    assert type(ret['_id']) == str

    t = time.time()
    for i in range(100000):
        jsonable(o)
    print(time.time() - t)

