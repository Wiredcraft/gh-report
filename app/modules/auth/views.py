from flask import Blueprint, session, render_template, url_for, redirect, request, jsonify, g, current_app
#from flask.ext.sqlalchemy import SQLAlchemy
from github import Github
from app.config import GITHUB_SESSION_TOKEN
from app.extensions import oauth

auth = Blueprint('auth', __name__)

def get_github():
    """ Create the connector to GitHub using the token """
    ghub = getattr(g, '_github', None)
    if ghub is None:
        ghub = g._github = Github(session.get(GITHUB_SESSION_TOKEN)[0])
    return ghub

def get_github_oauth():
    return oauth.remote_apps['github']

@auth.route('/')
def index():
    if GITHUB_SESSION_TOKEN in session:
        me = get_github_oauth().get('user')
        ghub = get_github()
        return render_template('options.html', username=me.data['login'])
    else:
        return render_template('index.html')

@auth.route('/login')
def login():
    if GITHUB_SESSION_TOKEN in session:
        me = get_github_oauth().get('user')
        return jsonify(me.data)
    return redirect(url_for('auth.authorize'))

@auth.route('/authorize')
def authorize():
    return get_github_oauth().authorize(callback=url_for('auth.authorized', _external=True))

@auth.route('/logout')
def logout():
    session.pop(GITHUB_SESSION_TOKEN, None)
    return redirect(url_for('auth.index'))

@auth.route('/login/authorized')
def authorized():
    resp = get_github_oauth().authorized_response()
    if resp is None:
        return 'Unable to authenticate due to %s - %s' % (
            request.args['error'],
            request.args['error_description']
        )
    session[GITHUB_SESSION_TOKEN] = (resp['access_token'], '')
    user = get_github_oauth().get('user')
    return jsonify(user.data)