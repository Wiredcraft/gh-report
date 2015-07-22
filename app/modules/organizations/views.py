from flask import Blueprint, render_template, current_app, request, g, redirect, url_for
from app.extensions import db
from app.modules.auth.views import get_github
from app.utils import login_required
from models import OrgDetails

orgs = Blueprint('organizations', __name__, url_prefix='/organizations')

@orgs.route('/add', methods=['POST'])
@login_required
def add():
    if request.args.get('name') != None:
        org = OrgDetails()
        org.org_name = request.args.get('name')
        org.username = g._user.login
        db.session.add(org)
        db.session.commit()
        redirect(url_for('auth.index'))
    else:
        return render_template('add.html')

@orgs.route('/<org_name>', methods=['GET'])
#@login_required
def view(org_name):
    get_github()
    from app.modules.api import OrganizationStats
    org = OrganizationStats(org_name)
    return render_template('organization.html', org=org, active_users=len(org.activity_per_user))