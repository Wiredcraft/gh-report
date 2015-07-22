from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask_oauthlib.client import OAuth
oauth = OAuth()

from flask_login import LoginManager
login_manager = LoginManager()
