from flask import Flask
from github import Github

def create_app():
    """ Creates our Flask app and loads it with the right config settings """
    app = Flask(__name__)

    # Load config file (default) or from the env-set location of the config file
    app.config.from_pyfile('config/gh-report.default.settings')
    app.config.from_envvar('GH_REPORT_SETTINGS')

    return app

def get_github():
    """ Create the connector to GitHub using the token """
    return Github(app.config['OAUTH_TOKEN'])

application = create_app()
ghub = get_github()