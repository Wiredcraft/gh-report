from github import Github
from flask import g, current_app

def get_github():
    """ Create the connector to GitHub using the token """
    ghub = getattr(g, '_github', None)
    if ghub is None:
        ghub = g._github = Github(current_app.config['OAUTH_TOKEN'])
    return ghub