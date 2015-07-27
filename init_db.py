import os
from flask import Flask
from app.app import load_config
from app.extensions import db

def init_db():
    """ Clean up and create database. """

    app = Flask(__name__)
    load_config(app)

    db.init_app(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.sqlite')
    with app.app_context():
        db.drop_all()
        db.create_all()

if __name__ == '__main__':
    init_db()