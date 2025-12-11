from flask import request, abort
import sqlalchemy
import datetime
from flask.json.provider import JSONProvider
import json


def get_int_from_url(name, default=0, min=0):
    """If field with name is not in the url query then default is returned,
    if it is there but it is not int or its less than min then abort(400)"""

    if request.args.get(name) == None:
        return default
    else:
        try:
            num = int(request.args.get(name))
            if num < min:
                raise Exception()
            return num
        except:
            abort(400)

def convert_to_id(id_str):
    id_ = int(id_str)
    
    if id_ < 0:
        raise ValueError("Id can't be less than 0")
    
    return id_

class UltraJSONProvider(JSONProvider):
    def __init__(self, app):
        super().__init__(app)

    def dumps(self, obj, **kwargs):
        return json.dumps(obj, default=ultra_serialize)

    def loads(self, obj_json, **kwargs):
        return json.loads(obj_json)


def ultra_serialize(obj):
    """This function procedure is as the following:\n
    1- returns obj._to_json() if it exists, note that _to_json should just return json serializable obj not json str\n
    2- returns obj.to_dict() if it exists,\n
    3- manually serializes some registered types if obj is instance of any of them.\n
    datetime -> str(datetime)\n
    sqlalchemy.Row -> obj._asdict()
    4- raises a value error if all the previous fails"""

    serialize_method_name = "_to_json"
    serialize_method = getattr(obj, serialize_method_name, None)
    if serialize_method != None and callable(serialize_method):
        return serialize_method()

    serialize_method_name = "to_dict"
    serialize_method = getattr(obj, serialize_method_name, None)
    if serialize_method != None and callable(serialize_method):
        return serialize_method()

    if isinstance(obj, datetime.datetime):
        return str(obj)

    if isinstance(obj, sqlalchemy.Row):
        return obj._asdict()

    raise Exception(f"Object {obj} of type {obj.__class__} can't be serialized")
