from sqlalchemy import Column
from app.extensions import db

class OrgDetails(db.Model):
    __tablename__ = 'org_details'

    username = Column(db.String, primary_key=True)
    org_name = Column(db.String, primary_key=True)

    def __init__(self, username=None, org_name=None):
        self.username = username
        self.org_name = org_name

    # Determines whether or not we're done loading the stats for the org
    done = Column(db.Boolean)

class Commit(db.Model):
    __tablename__ = 'commits'

    username = Column(db.String)
    repo = Column(db.String)
    org = Column(db.String)
    time = Column(db.DateTime)
    adds = Column(db.Integer)
    deletes = Column(db.Integer)
    changes = Column(db.Integer)
    sha = Column(db.String, primary_key=True)

    def __init__(self, username, repo, org, time, adds, deletes, changes, sha):
        self.username = username
        self.repo = repo
        self.org = org
        self.time = time
        self.adds = adds
        self.deletes = deletes
        self.changes = changes
        self.sha = sha

class Issue(db.Model):
    __tablename__ = 'issues'

    username = Column(db.String)
    id = Column(db.Integer, primary_key=True)
    repo = Column(db.String)
    org = Column(db.String)
    created_at = Column(db.DateTime)

    def __init__(self, username, id, repo, org, created_at):
        self.username = username
        self.id = id
        self.repo = repo
        self.org = org
        self.created_at = created_at

class IssueComment(db.Model):
    __tablename__ = 'issue_comments'

    username = Column(db.String)
    id = Column(db.Integer, primary_key=True)
    repo = Column(db.String)
    org = Column(db.String)
    created_at = Column(db.DateTime)

    def __init__(self, username, id, repo, org, created_at):
        self.username = username
        self.id = id
        self.repo = repo
        self.org = org
        self.created_at = created_at

class OrgReports(db.Model):
    __tablename__ = 'org_reports'

    username = Column(db.String)
    org_name = Column(db.String, primary_key=True)
    timestamp = Column(db.DateTime, primary_key=True)