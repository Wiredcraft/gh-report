import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
render_template, flash, json, Response
import datetime

from collections import defaultdict

from github import Github

app = Flask(__name__)
app.config['DEBUG'] = True

class MemberStats(object):
    def __init__(self, commits):
        self.number_of_commits = len(commits)
        self.total_additions = sum(map(lambda commit: commit.stats.additions, commits))
        self.total_deletions = sum(map(lambda commit: commit.stats.additions, commits))
        self.total_changes = sum(map(lambda commit: commit.stats.total, commits))

@app.route('/_commits')
def count_commits():
    g = Github("b736b1b52904e45adfd58d076f2a6ef514fb7a5f")
    repo = g.get_repo("django/django")
    counts = defaultdict(list)
    for commit in repo.get_commits(since=datetime.datetime(2015, 7, 9, 16, 30)):
        counts[commit.committer.name].append(commit)
        
    for name in counts.keys():
        counts[name] = MemberStats(counts[name]).__dict__
    return Response(json.dumps(counts), mimetype='application/json')


if __name__ == '__main__':
    app.run()
