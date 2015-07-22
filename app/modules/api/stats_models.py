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
    def __init__(self, commits_username, org, commit_count, adds, deletes, changes, changes_per_commit, issue_count):
        self.username = commits_username
        self.org = org
        self.commits = commit_count if commit_count != None else 0
        self.adds = adds if adds != None else 0
        self.deletes = deletes if deletes != None else 0
        self.changes = changes if changes != None else 0
        self.changes_per_commit = changes_per_commit
        self.issues = issue_count if issue_count != None else 0
        self.activity_score = 0.0

"""
Represents user activity stats for a repository
"""
class UserActivityRepo(UserActivity):
    def __init__(self, commits_username, org, commit_count, adds, deletes, changes, changes_per_commit, issue_count, repo):
        super(UserActivityRepo, self).__init__(commits_username, org, commit_count, adds, deletes, changes, changes_per_commit, issue_count)
        self.repo = repo
