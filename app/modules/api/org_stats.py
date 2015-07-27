from collections import defaultdict
from datetime import timedelta, date, datetime
from github import GithubException
from sqlalchemy import func
from app.modules.api.stats_models import UserActivity, UserActivityRepo, RepositoryActivity
from app.modules.auth.views import get_github_oauth
from app.modules.organizations.models import Commit, OrgReports, Issue, IssueComment, Member
from app.extensions import db
from flask import g

class OrganizationStats(object):

    def __init__(self, org_name):
        self.org_name = str(org_name)
        self.org = g._github.get_organization(org_name)

    def load_all(self):
        """ Loads various statistics for this organization over the past week. If the data has already been
        loaded to the database, it pulls it from the database. Otherwise, it queries GitHub and stores it
        in the database. """

        self.since = (date.today() - timedelta(days=7))
        self.until = date.today()

        org_report = OrgReports(org_name=self.org_name, timestamp=self.until.strftime("%Y-%m-%d %H:%M:%S.000000"))
        if org_report.has_current_data() == False:
            self._load_activity_from_api()

    def _load_member_from_api(self, login, avatar_url):
        author = Member(login, avatar_url, self.org_name)
        db.session.merge(author)
        db.session.commit()

    def record_loaded_data(self):
        """ Record that data load from the API for a given organization and date has taken place. """
        org_report = OrgReports(get_github_oauth().get('user').data['login'], self.org_name, date.today())
        db.session.merge(org_report)
        db.session.commit()

    def _load_activity_from_api(self):
        """ Loads information about commits from the GitHub API into the database """

        for repo in self.org.get_repos():
            try:
                for commit in repo.get_commits(since=datetime.combine(self.since, datetime.min.time())):
                    commit_time = datetime.strptime(commit.last_modified, "%a, %d %b %Y %H:%M:%S %Z")

                    some_commit = Commit(commit.author.login, repo.name, repo.organization.login,\
                                         commit_time, commit.stats.additions, commit.stats.deletions,\
                                         commit.stats.total, commit.sha)

                    db.session.merge(some_commit)
                    db.session.commit()
                    self._load_member_from_api(commit.author.login, commit.author.avatar_url)

                for issue in repo.get_issues(since=datetime.combine(self.since, datetime.min.time())):
                    some_issue = Issue(issue.user.login, issue.id, repo.name, repo.organization.name, issue.created_at)
                    db.session.merge(some_issue)
                    db.session.commit()
                    self._load_member_from_api(issue.user.login, issue.user.avatar_url)

                for issue_comment in repo.get_issues_comments(since=datetime.combine(self.since, datetime.min.time())):
                    some_issue_comment = IssueComment(issue_comment.user.login, issue_comment.id, repo.name, repo.organization.name, issue_comment.created_at)
                    db.session.merge(some_issue_comment)
                    db.session.commit()
                    self._load_member_from_api(issue_comment.user.login, issue_comment.user.avatar_url)

            except GithubException as e:
                print e.data, e.message

        self.record_loaded_data()

    def get_user_activity(self):
        """ Loads the activity for each member in the organization. """
        activity_per_user = []

        for member in Member.get_members_in_org(self.org_name):
            username, avatar_url = map(lambda x: str(x), member)
            commit_info = Commit.get_commit_stats(username, self.org_name).one()
            issue_info = Issue.get_issue_stats(username, self.org_name).one()
            issue_comments_info = IssueComment.get_issue_comment_stats(username, self.org_name).one()

            activity_per_user.append(UserActivity(commits_username=username,\
                                                  org=self.org_name,\
                                                  commit_count=commit_info[1],\
                                                  changes=commit_info[2],\
                                                  issue_count=issue_info[1],\
                                                  issue_comments=issue_comments_info[1],\
                                                  avatar_url=avatar_url))
        return self._calculate_metrics(activity_per_user)

    def get_user_repo_activity(self, username):
        """ Retrieves user activity per repository within the organization (based on commits,
            code changes, issue comments/creation) from the database. """

        activity = []
        commits = self.create_repo_dict(Commit.get_commit_stats(username, self.org_name).group_by(Commit.repo))
        issues = self.create_repo_dict(Issue.get_issue_stats(username, self.org_name).group_by(Issue.repo))
        issue_comments = self.create_repo_dict(IssueComment.get_issue_comment_stats(username, self.org_name).group_by(IssueComment.id))

        repositories = set(commits.keys() + issues.keys()+ issue_comments.keys())

        for repo in repositories:
            activity.append(UserActivityRepo(repo=repo, commits_username=username,\
                 commit_count=(commits[repo][0] if repo in commits else 0),\
                 org=self.org_name,\
                 changes=(commits[repo][1] if repo in commits else 0),\
                 issue_count=(issues[repo][0] if repo in issues else 0),\
                 issue_comments=(issue_comments[repo][0] if repo in issue_comments else 0)))

        activity = self._calculate_metrics(activity)
        return activity

    def create_repo_dict(self, lst):
        return {item[0]: item[1:] for item in lst}


    def get_repositories(self):
        commits = self.create_repo_dict(db.session.query(Commit.repo, func.count(Commit.sha), func.sum(Commit.changes))\
            .filter(Commit.org.like(self.org_name))\
            .group_by(Commit.repo).all())
        issues = self.create_repo_dict(db.session.query(Issue.repo, func.count(Issue.id))\
            .filter(Issue.org.like(self.org_name))\
            .group_by(Issue.repo).all())
        issue_comments = self.create_repo_dict(db.session.query(IssueComment.repo, func.count(IssueComment.id))\
            .filter(IssueComment.org.like(self.org_name))\
            .group_by(IssueComment.repo).all())
        repos = set(commits.keys() + issues.keys()+ issue_comments.keys())
        repositories = []
        for repo in repos:
            repositories.append(\
                RepositoryActivity(repo=repo, org=self.org_name,\
                   commits=commits[repo][0] if repo in commits else 0,\
                   changes=commits[repo][1] if repo in commits else 0,\
                   issues=issues[repo][0] if repo in issues else 0,\
                   issue_comments=issue_comments[repo][0] if repo in issue_comments else 0))
        return repositories

    def get_repo_users(self):
        repo_users = defaultdict(list)
        for repo in self.get_repositories():
            commit_repos = self.create_repo_dict(db.session.query(Commit.username, func.count(Commit.sha), func.sum(Commit.changes))\
                .filter(Commit.org.like(self.org_name)).filter(Commit.repo.like(repo.name)).group_by(Commit.username).all())
            issue_repos = self.create_repo_dict(db.session.query(Issue.username, func.count(Issue.id))\
                .filter(Issue.org.like(self.org_name)).filter(Issue.repo.like(repo.name)).group_by(Issue.repo, Issue.username).all())
            issue_comment_repos = self.create_repo_dict(db.session.query(IssueComment.username, func.count(IssueComment.id))\
                .filter(IssueComment.org.like(self.org_name)).filter(IssueComment.repo.like(repo.name)).group_by(IssueComment.repo, IssueComment.username).all())

            users = set(commit_repos.keys() + issue_repos.keys()+ issue_comment_repos.keys())
            for user in users:
                if user in commit_repos and commit_repos[user][1] > 0:
                    user_activity = UserActivityRepo(repo=repo.name,\
                                      org=self.org_name,\
                                      commits_username=user,\
                                      changes=commit_repos[user][1] if user in commit_repos else 0,\
                                      commit_count=commit_repos[user][0] if user in commit_repos else 0,\
                                      issue_count=issue_repos[user][0] if user in issue_repos else 0,\
                                      issue_comments=issue_comment_repos[user][0] if user in issue_comment_repos else 0)
                    user_activity.percent_changes = user_activity.changes/float(repo.changes)
                    user_activity.percent_issues = user_activity.issues/float(repo.issues)
                    user_activity.percent_issue_comments = user_activity.issue_comments/float(repo.issue_comments)
                    repo_users[repo.name].append(user_activity)
        return repo_users


    def _calculate_metrics(self, activity):
        """ Calculates the normalized activity score based on the lines of code changed and issues created. """

        for i in range(len(activity)):
            activity[i].changes_score = activity[i].normalize(activity, lambda x: x.changes)
            activity[i].issues_score = activity[i].normalize(activity, lambda x: x.issues)
            activity[i].issue_comments_score = activity[i].normalize(activity, lambda x: x.issue_comments)
            activity[i].activity_score = (activity[i].changes_score + activity[i].issues_score + activity[i].issue_comments_score)

        total_changes = float(sum(map(lambda x: x.changes, activity)))
        total_issues = float(sum(map(lambda x: x.issues, activity)))
        total_issue_comments = float(sum(map(lambda x: x.issue_comments, activity)))

        for i in range(len(activity)):
            activity[i].percent_changes = activity[i].changes / total_changes if total_changes != 0 else 0
            activity[i].percent_issues = activity[i].issues / total_issues if total_issues != 0 else 0
            activity[i].percent_issue_comments = activity[i].issue_comments / total_issue_comments if total_issue_comments != 0 else 0
            activity[i].percent = (activity[i].percent_changes + activity[i].percent_issues + activity[i].percent_issue_comments)/3.0
            activity[i].activity_score_normalized = activity[i].normalize(activity, lambda x: x.activity_score)*100.0

        activity = sorted(activity, key=lambda x: x.activity_score, reverse=True)
        return activity