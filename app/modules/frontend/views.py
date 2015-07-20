from flask import Blueprint, render_template, current_app, request, flash, g
from github import Github
from app.modules.api import OrganizationStats
from app.modules.api.ghub import get_github

frontend = Blueprint('frontend', __name__, url_prefix='/')
