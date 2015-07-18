import operator
from app import ghub
from app.modules.api.repository import RepositoryStats, SortedCommiters
from app.modules.api.stats import MemberCommitStats


class OrganizationStats(object):

    def __init__(self, org_name):
        self.org_name = org_name
        self.org = ghub.get_organization(org_name)

        self.committers = self.load_committers()
        self.sorted_committers = SortedCommiters(self.committers)

    def load_committers(self):
        org_ommitters = {}
        for repo in self.org.get_repos():
            org_ommitters = self.__sum_stat_dicts(RepositoryStats(repo).committers, org_ommitters)
        return org_ommitters

    def __sum_stat_dicts(A, B):
        return { x: A.get(x, MemberCommitStats([])).plus(B.get(x, None)) for x in set(A).union(B) }