import os

__package__ = 'app'

from flask import Flask, g, session
from .configuration import GITHUB_SESSION_TOKEN
from .extensions import oauth, db
from modules.organizations.views import orgs
from modules.auth.views import auth

def create_app():
    """Creates our Flask app and loads it with the right config settings"""
    app = Flask(__name__)

    load_config(app)
    load_extensions(app)
    load_github_oauth(app)

    ALL_BLUEPRINTS = (
        orgs, auth
    )

    load_blueprints(app, ALL_BLUEPRINTS)

    return app

def load_config(app):
    """Load config from file (default) or from the env-set location of the config file."""

    app.config.from_pyfile('config/gh-report.default.settings', silent=True)


def load_extensions(app):
    """Configure extensions for app"""
    db.init_app(app)
    oauth.init_app(app)

def load_github_oauth(app):
    ghauth = oauth.remote_app('github',
        consumer_key=app.config['GITHUB_KEY'],
        consumer_secret=app.config['GITHUB_SECRET'],
        request_token_params={'scope': 'public_repo,repo,read:org'},
        base_url='https://api.github.com/',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize')
    ghauth.tokengetter(get_github_oauth_token)
    return ghauth

def get_github_oauth_token():
    return session.get(GITHUB_SESSION_TOKEN)

def load_blueprints(app, blueprints):
    """Configure all blueprints."""

    for blueprint in blueprints:
        app.register_blueprint(blueprint)