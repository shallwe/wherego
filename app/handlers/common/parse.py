# coding:utf-8
from datetime import datetime

import bson
from bson import ObjectId
import mongoengine


def jsonable(o):
    """
    将对象转化为能直接json_encode的对象，
    根据自己的需要添加其他的类型
    """
    t = type(o)
    if t == dict:
        return {k: jsonable(o[k]) for k in o}
    elif t in (list, tuple, set):
        return [jsonable(_) for _ in o]
    elif t == datetime:
        return str(o)
    elif t == ObjectId:
        return str(o)
    elif t == bson.SON:
        return jsonable(o.to_dict())
    elif isinstance(o, mongoengine.Document):
        return {
            k: jsonable(getattr(o, k))
            for k in o._fields
            if getattr(o, k) is not None
            }
    elif t == bson.DBRef:
        return {
            "_ref": {
                o.collection: str(o.id)
            }
        }
    else:
        return o