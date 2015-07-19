
from app.utils import Struct

class MemberCommitStats(object):
    """ Keeps record of the commit statistics for a given member """
    def __init__(self, commits):
        self.number_of_commits = len(commits)
        self.additions = sum(map(lambda commit: commit.stats.additions, commits))
        self.deletions = sum(map(lambda commit: commit.stats.additions, commits))
        self.changes = sum(map(lambda commit: commit.stats.total, commits))

    def plus(self, obj):
        if obj is None:
            return obj
        else:
            internal_dict = {'number_of_commits': self.number_of_commits + obj.number_of_commits,\
                         'additions': self.additions + obj.additions,\
                         'deletions': self.deletions + obj.deletions,\
                         'changes': self.changes + obj.changes}
            return Struct(**internal_dict)


class MemberIssueStats(object):
    """ Keeps record of the issue-related statistics for a given member """
    def __init__(self):
        self.created = ""
        self.commented = ""
        self.closed = ""


"""
@app.route('/_commits')
def count_commits():
    since = time.strptime(request.args.get('since'), "%Y-%m-%d %H:%M:%S")
    repo_stats = RepositoryStats(app.config['REPO_NAME'])
    commit_stats_per_user = repo_stats.load_commits(since)

    return Response(json.dumps(commit_stats_per_user), mimetype='application/json')
"""