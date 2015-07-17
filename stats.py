import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
render_template, flash, json, Response
import datetime, time

from collections import defaultdict

from github import Github

app = Flask(__name__)
app.config['DEBUG'] = True

# TODO: config file this
ghub = Github("b736b1b52904e45adfd58d076f2a6ef514fb7a5f")

class MemberStats(object):
    def __init__(self, commits):
        self.number_of_commits = len(commits)
        self.total_additions = sum(map(lambda commit: commit.stats.additions, commits))
        self.total_deletions = sum(map(lambda commit: commit.stats.additions, commits))
        self.total_changes = sum(map(lambda commit: commit.stats.total, commits))

class RepositoryStats(object):
    def __init__(self, repo_name):
        self.repo = ghub.get_repo(repo_name)
        self.commits = {}
        
    def get_commits(self, since_time):
        commits_per_user = defaultdict(list)
        for commit in self.repo.get_commits(since=since_time):
            commits_per_user[commit.committer.login].append(commit)
        for name in counts.keys():
            commits_per_user[name] = MemberStats(counts[name]).__dict__
        return commits_per_user
        

@app.route('/_commits')
def count_commits():
    since = time.strptime(request.args.get('since'), "%Y-%m-%d %H:%M:%S")    

    # TODO: make the repo name customizable
    repo_stats = RepositoryStats("django/django")
    commit_stats_per_user = repo_stats.get_commits(since)
    
    return Response(json.dumps(commit_stats_per_user), mimetype='application/json')


if __name__ == '__main__':
    app.run()
