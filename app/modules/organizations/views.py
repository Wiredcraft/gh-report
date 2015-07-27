from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.modules.auth.views import get_github, get_github_oauth
from app.utils import login_required

orgs = Blueprint('organizations', __name__, url_prefix='/organizations')

@orgs.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """ Loads an organization to the database from the GitHub API """
    username = get_github_oauth().get('user').data['login']
    if request.method == 'POST':
        from app.modules.api import OrganizationStats
        org_name = request.form['org_name']
        get_github()

        org = OrganizationStats(org_name)
        org.load_all()
        return redirect(url_for('organizations.view', org_name=org_name))
    else:
        return render_template('add_org.html', username=username)

@orgs.route('/view/<org_name>', methods=['GET'])
@login_required
def view(org_name):
    """ Displays an organization brief """
    get_github()
    from app.modules.api import OrganizationStats
    org = OrganizationStats(org_name)
    activity_per_user = org.get_user_activity()
    repo_activity = org.get_repo_users()
    repositories = org.get_repositories()
    return render_template('organization.html', activity_per_user=activity_per_user, org_name=org_name, repositories=repositories, repo_activity=repo_activity)

@orgs.route('/repo_data/<org_name>/<username>', methods=['GET'])
def repo_data(org_name, username):
    """ Retrieves user activity statistics for a given org and groups the data by repository. """
    get_github()
    from app.modules.api import OrganizationStats
    org = OrganizationStats(org_name)
    return jsonify(repositories=map(lambda x: x.__dict__, org.get_user_repo_activity(username)))