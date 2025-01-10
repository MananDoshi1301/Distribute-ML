import functools
from flask import jsonify

def return_response(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        res, statuscode = func(*args, **kwargs)
        return jsonify(res, statuscode)
    return wrapper