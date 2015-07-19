from flask import Blueprint, render_template, current_app, request, flash, g
from github import Github
from app.modules.api import OrganizationStats
from app.modules.api.ghub import get_github

orgs = Blueprint('organizations', __name__, url_prefix='/organizations')

@orgs.route('/add', methods=['POST'])
def add():
    pass

@orgs.route('/team', methods=['GET'])
def team():
    get_github()
    name = request.args.get('id')
    org = OrganizationStats(name)
    most_active = org.sorted_committers.get_most_active(10)
    print most_active
    return render_template('team_stats.html', most_active=most_active)