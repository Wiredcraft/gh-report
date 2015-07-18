from flask import Blueprint, render_template, current_app, request, flash

orgs = Blueprint('organizations', __name__, url_prefix='/organizations')

@orgs.route('/add', methods=['POST'])
def add():
    pass

@orgs.route('/team', methods=['GET'])
def team():
    pass