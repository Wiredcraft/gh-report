from sqlalchemy import Column, func
from app.extensions import db

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

    @staticmethod
    def get_commit_stats(username, org):
        return db.session.query(Commit.repo, func.count(Commit.sha), func.sum(Commit.changes))\
                .filter(Commit.username.like(username))\
                .filter(Commit.org.like(org))

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

    @staticmethod
    def get_issue_stats(username, org_name):
        return db.session.query(Issue.repo, func.count(Issue.id)).\
                filter(Issue.username.like(username)).\
                filter(Issue.org.like(org_name))

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

    @staticmethod
    def get_issue_comment_stats(username, org_name):
        return db.session.query(IssueComment.repo, func.count(IssueComment.id))\
                .filter(IssueComment.username.like(username))\
                .filter(IssueComment.org.like(org_name))

class OrgReports(db.Model):
    """ Determines whether or not we're done loading the stats for the org. """
    __tablename__ = 'org_reports'

    username = Column(db.String)
    org_name = Column(db.String, primary_key=True)
    timestamp = Column(db.DateTime, primary_key=True)

    def __init__(self, username, org_name, timestamp):
        self.username = username
        self.org_name = org_name
        self.timestamp = timestamp

    def has_current_data(self):
        reports = db.session.query(OrgReports).filter_by(org_name=self.org_name, timestamp=self.timestamp)
        return reports.count() > 0

class Member(db.Model):
    __tablename__ = 'members'

    username = Column(db.String, primary_key=True)
    avatar_url = Column(db.String)
    org = Column(db.String, primary_key=True)

    def __init__(self, username, avatar_url, org):
        self.username = username
        self.avatar_url = avatar_url
        self.org = org

    @staticmethod
    def get_members_in_org(org_name):
        return db.session.query(Member.username, Member.avatar_url).filter(Member.org.like(org_name)).all();

    @staticmethod
    def get_avatar_url(username):
        return db.session.query(Member.avatar_url).filter(Member.username.like(username)).all()[0];