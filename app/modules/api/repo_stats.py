import operator
from datetime import datetime
from stats import MemberCommitStats, MemberIssueStats
from collections import defaultdict

"""
Represents statistics about a given repository.
"""
class RepositoryStats(object):
    def __init__(self, repo):
        self.repo = repo
        self.name = self.repo.name
        self.committers = self.load_commits("2015-07-10 00:00:00")
        self.sorted_committers = SortedCommiters(self.committers)
        self.number_of_committers = len(self.sorted_committers.committers)
        
    def load_commits(self, since_time):
        commits_per_user = defaultdict(list)
        try:
            for commit in self.repo.get_commits(since=datetime.strptime(since_time, "%Y-%m-%d %H:%M:%S")):
                commits_per_user[commit.committer.login].append(commit)
            for name in commits_per_user.keys():
                commits_per_user[name] = MemberCommitStats(commits_per_user[name])
        except:
            pass
        return commits_per_user

    def load_issues(self, since_time):
        issues_per_user = defaultdict(list)

class SortedCommiters(object):
    def __init__(self, committers):
        if len(committers.keys()) == 0:
            self.committers = []
        else:
            self.committers = sorted(committers.items(), key=lambda x: x[1].number_of_commits, reverse=True)
        self.most_active = self.get_most_active(10)
        self.least_active = self.get_least_active(10)

    def get_most_active(self, n):
        return self.committers[:min(n, len(self.committers))]

    def get_least_active(self, n):
        return self.committers[len(self.committers) - max(0, n):]

