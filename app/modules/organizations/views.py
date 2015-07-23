from flask import Blueprint, render_template, current_app, request, g, redirect, url_for
from app.extensions import db
from app.modules.auth.views import get_github, get_github_oauth
from app.utils import login_required
from models import OrgReports
from datetime import date

orgs = Blueprint('organizations', __name__, url_prefix='/organizations')

@orgs.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    username = get_github_oauth().get('user').data['login']
    if request.method == 'POST':
        from app.modules.api import OrganizationStats
        org_name = request.form['org_name']
        get_github()

        org = OrganizationStats(org_name)

        org_report = OrgReports(username, org_name, date.today())
        db.session.merge(org_report)
        db.session.commit()

        return redirect(url_for('organizations.view', org_name=org_name))
    else:
        return render_template('add_org.html', username=username)

@orgs.route('/view/<org_name>', methods=['GET'])
@login_required
def view(org_name):
    get_github()
    me = get_github_oauth().get('user')

    from app.modules.api import OrganizationStats
    org = OrganizationStats(org_name)

    return render_template('organization.html', org=org, active_users=len(org.activity_per_user), username=me.data['login'])