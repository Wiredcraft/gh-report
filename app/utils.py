from functools import wraps
from flask import g, redirect, url_for, request, session
from .configuration import GITHUB_SESSION_TOKEN

class Struct(object):
        def __init__(self, **entries):
            self.__dict__.update(entries)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if GITHUB_SESSION_TOKEN not in session:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
