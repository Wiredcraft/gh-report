"""
Represents information about activity levels within an organization or repository.
"""
class Activity(object):

    def normalize(self, values, key_func):
        """ Normalizes the given value against all other values for this metric. """
        min_value = min(map(key_func, values))
        max_value = max(map(key_func, values))
        if max_value - min_value == 0:
            return 0.0
        return (float(key_func(self)) - min_value)/(max_value - min_value)

"""
Represents user activity stats in an organization
"""
class UserActivity(Activity):
    def __init__(self, commits_username, org, commit_count = 0, adds = 0, deletes = 0, changes = 0, issue_count = 0, issue_comments = 0, avatar_url=None):
        self.username = commits_username
        self.org = org
        self.commits = commit_count
        self.adds = adds
        self.deletes = deletes
        self.changes = changes if changes != None else 0
        self.issues = issue_count
        self.activity_score = 0.0
        self.avatar_url = avatar_url if avatar_url != None else self.get_avatar_url()
        self.issue_comments = issue_comments

    def get_avatar_url(self):
        from app.extensions import db
        result = db.engine.execute("SELECT avatar_url FROM members WHERE username = '%s';" % self.username).fetchone()
        if result != None:
            return result[0]
        return ''


"""
Represents user activity stats for a repository
"""
class UserActivityRepo(UserActivity):
    def __init__(self, commits_username, org, repo, commit_count = 0, adds = 0, deletes = 0, changes = 0, issue_count = 0, issue_comments = 0, avatar_url = None):
        super(UserActivityRepo, self).__init__(commits_username, org, commit_count, adds, deletes, changes, issue_count, issue_comments, avatar_url)
        self.repo = repo

class RepositoryActivity(object):
    def __init__(self, repo, org, commits, changes, issues, issue_comments):
        self.name = repo
        self.org = org
        self.commits = commits
        self.changes = changes
        self.issues = issues
        self.issue_comments = issue_comments