from functools import wraps
from flask import g, redirect, url_for, request


class Struct(object):
        def __init__(self, **entries):
            self.__dict__.update(entries)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
