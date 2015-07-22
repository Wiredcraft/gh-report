from collections import defaultdict
from datetime import timedelta, date, datetime
from github import GithubException
from app.modules.api.stats_models import UserActivity, UserActivityRepo
from app.modules.organizations.models import Commit, OrgReports, Issue, IssueComment
from app.extensions import db
from flask import g

class OrganizationStats(object):

    def __init__(self, org_name):
        self.org_name = str(org_name)
        self.org = g._github.get_organization(org_name)

        self.load_all()

    def load_all(self):
        """ Loads various statistics for this organization over the past week. If the data has already been
        loaded to the database, it pulls it from the database. Otherwise, it queries GitHub and stores it
        in the database. """

        self.since = (date.today() - timedelta(days=7))
        self.until = date.today()

        reports = db.session.query(OrgReports).filter_by(org_name=self.org_name, timestamp=self.until.strftime("%Y-%m-%d %H:%M:%S.000000"))
        if reports.count() == 0:
            self._load_committers_from_api()
            self._load_issues_from_api()

        self._load_activity_from_db()

    def _load_committers_from_api(self):
        """ Loads information about commits from the GitHub API into the database """

        for repo in self.org.get_repos():
                try:
                    for commit in repo.get_commits(since=datetime.combine(self.since, datetime.min.time())):
                        commit_time = datetime.strptime(commit.last_modified, "%a, %d %b %Y %H:%M:%S %Z")

                        some_commit = Commit(commit.committer.login, repo.name, repo.organization.name,\
                                             commit_time, commit.stats.additions, commit.stats.deletions,\
                                             commit.stats.total, commit.sha)

                        db.session.merge(some_commit)
                        db.session.commit()
                except GithubException as e:
                    print e.data, e.message

    def _load_issues_from_api(self):
        """ Loads both issues and issue comments from the GitHub API """

        for repo in self.org.get_repos():
            try:
                for issue in repo.get_issues(since=datetime.combine(self.since, datetime.min.time())):
                    some_issue = Issue(issue.user.login, issue.id, repo.name, repo.organization.name, issue.created_at)
                    db.session.merge(some_issue)
                    db.session.commit()

                for issue_comment in repo.get_issues_comments(since=datetime.combine(self.since, datetime.min.time())):
                    some_issue_comment = IssueComment(issue_comment.user.login, issue_comment.id, repo.name, repo.organization.name, issue_comment.created_at)
                    db.session.merge(some_issue_comment)
                    db.session.commit()

            except GithubException as e:
                print e.data, e.message

    def _load_activity_from_db(self):
        """" Loads issues and comments from the database """

        per_user_and_repo = db.engine.execute("SELECT commits.username AS commits_username, commits.org AS org,  commits.repo AS repo,  count(commits.sha) AS commit_count,  sum(commits.adds) AS adds,  sum(commits.deletes) AS deletes,  sum(commits.changes) AS changes,  sum(commits.changes) / count(commits.username) AS changes_per_commit, count(issues.id) AS issue_count  FROM commits LEFT JOIN issues ON commits.username = issues.username AND commits.org = issues.org AND commits.repo = issues.repo GROUP BY commits_username, commits.org, commits.repo UNION  SELECT issues.username as issues_username,  issues.org AS org,  issues.repo AS repo, count(commits.sha) AS commit_count,  sum(commits.adds) AS adds,  sum(commits.deletes) AS deletes,  sum(commits.changes) AS changes,  sum(commits.changes) / count(commits.username) AS changes_per_commit, count(issues.id) AS issue_count  FROM issues LEFT JOIN commits ON commits.username = issues.username AND commits.org = issues.org AND commits.repo = issues.repo GROUP BY issues_username, issues.org, issues.repo;")
        per_user = db.engine.execute("SELECT commits.username AS commits_username, commits.org AS org,  count(commits.sha) AS commit_count,  sum(commits.adds) AS adds,  sum(commits.deletes) AS deletes,  sum(commits.changes) AS changes,  sum(commits.changes) / count(commits.username) AS changes_per_commit, count(issues.id) AS issue_count  FROM commits LEFT JOIN issues ON commits.username = issues.username AND commits.org = issues.org  GROUP BY commits_username, commits.org UNION  SELECT issues.username as issues_username,  issues.org AS org,  count(commits.sha) AS commit_count,  sum(commits.adds) AS adds,  sum(commits.deletes) AS deletes,  sum(commits.changes) AS changes,  sum(commits.changes) / count(commits.username) AS changes_per_commit, count(issues.id) AS issue_count  FROM issues LEFT JOIN commits ON commits.username = issues.username AND commits.org = issues.org  GROUP BY issues_username, issues.org;")

        # Loads user activity stats for the organization overall
        self.activity_per_user, self.activity_per_user_and_repo = [], defaultdict(list)
        for r in per_user:
            self.activity_per_user.append(UserActivity(**r))
        self.activity_per_user = self._calculate_metrics(self.activity_per_user)

        # Loads user activity stats for each repository in the organization
        for r in per_user_and_repo:
            self.activity_per_user_and_repo[r['repo']].append(UserActivityRepo(**r))
        for repo in self.activity_per_user_and_repo:
            self.activity_per_user_and_repo[repo] = self._calculate_metrics(self.activity_per_user_and_repo[repo])

    def _calculate_metrics(self, activity):
        """ Calculates the normalized activity score based on the lines of code changed and issues created. """

        for i in range(len(activity)):
            activity[i].changes_score = activity[i].normalize(activity, lambda x: x.changes)
            activity[i].issues_score = activity[i].normalize(activity, lambda x: x.issues)
            activity[i].activity_score = (activity[i].changes_score + activity[i].issues_score)

        for i in range(len(activity)):
            activity[i].activity_score_normalized = activity[i].normalize(activity, lambda x: x.activity_score)*100.0

        activity = sorted(activity, key=lambda x: x.activity_score, reverse=True)
        return activity