import operator
from repo_stats import RepositoryStats, SortedCommiters
from stats import MemberCommitStats
from flask import g

class OrganizationStats(object):

    def __init__(self, org_name):
        self.org_name = org_name
        self.org = g._github.get_organization(org_name)

        self.committers = self.__load_committers()
        self.sorted_committers = SortedCommiters(self.committers)

    def __load_committers(self):
        org_committers = {}
        for repo in self.org.get_repos():
            repo_committers = RepositoryStats(repo).committers
            org_committers = self.__sum_stat_dicts(repo_committers, org_committers)
        return org_committers

    def __sum_stat_dicts(self, A, B):
        return { x: A.get(x, MemberCommitStats([])).plus(B.get(x, MemberCommitStats([]))) for x in set(A).union(B) }