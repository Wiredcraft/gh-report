import operator
from app import ghub
from stats import MemberCommitStats, MemberIssueStats
from collections import defaultdict

"""
Represents statistics about a given repository.
"""
class RepositoryStats(object):
    def __init__(self, repo):
        self.repo = repo
        self.committers = self.load_commits("####")
        self.sorted_committers = SortedCommiters(self.committers)
        
    def load_commits(self, since_time):
        commits_per_user = defaultdict(list)
        for commit in self.repo.get_commits(since=since_time):
            commits_per_user[commit.committer.login].append(commit)
        for name in commits_per_user.keys():
            commits_per_user[name] = MemberCommitStats(commits_per_user[name]).__dict__
        return commits_per_user

    def load_issues(self, since_time):
        issues_per_user = defaultdict(list)

class SortedCommiters(object):
    def __init__(self, committers):
        self.committers = sorted(committers.items(), key=operator.itemgetter(1).number_of_commits)

    def get_most_active(self, n):
        return self.committers[:min(n, len(self.sorted_committers))]
    
    def get_least_active(self, n):
        return self.committers[len(self.sorted_committers) - max(0, n):]

