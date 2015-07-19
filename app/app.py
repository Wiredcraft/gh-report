from flask import Flask, g
from modules.organizations.views import orgs

ALL_BLUEPRINTS = (
    orgs,
)

def create_app():
    """ Creates our Flask app and loads it with the right config settings """
    app = Flask(__name__)

    load_config(app)
    configure_blueprints(app, ALL_BLUEPRINTS)

    return app

def load_config(app):
    """Load config from file (default) or from the env-set location of the config file."""

    app.config.from_pyfile('config/gh-report.default.settings', silent=True)
    #app.config.from_envvar('GH_REPORT_SETTINGS')


def configure_blueprints(app, blueprints):
    """Configure all blueprints."""

    for blueprint in blueprints:
        app.register_blueprint(blueprint)