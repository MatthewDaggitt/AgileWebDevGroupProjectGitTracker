from collections import defaultdict
from github import Github
from github import Auth
import os
import sys

MAX_COMMITS_TO_DISPLAY = 50
MAX_ISSUES_TO_DISPLAY = 50
MAX_PRS_TO_DISPLAY = 50
TOKEN = os.environ.get("GITHUB_ACCESS_TOKEN")

auth = Auth.Token(TOKEN)

repo_url = sys.argv[1]


g = Github(auth=auth)
limit = g.get_rate_limit().core
print(f"Hourly queries: {limit.limit}")
print(f"Queries remaining: {limit.remaining}")

print(f"Repo URL: {repo_url}")
repo = g.get_repo(repo_url)

#####################
## Commit scraping ##
#####################
print(f"Scraping commit data...")
all_commits = repo.get_commits()
commits_by_usr = defaultdict(list)
for commit in all_commits:
    commits_by_usr[commit.author].append(commit)

print(f"\n\n")
print(f"============")
print(f"Commit marks")
print(f"============")

for (user, user_commits) in commits_by_usr.items():
    print(f"\n")
    print(f"============")
    print(f"User: {user.login}")
    print(f"Total number: {len(user_commits)}")
    for id, user_commit in enumerate(user_commits[:MAX_COMMITS_TO_DISPLAY]):
        print(f"\n{id}. {user_commit.commit.message}")
    if len(user_commits) > MAX_COMMITS_TO_DISPLAY:
        print("... cutting off remaining commits")

####################
## Issue scraping ##
####################
print(f"\n\n")
print(f"Scraping issue data...")
all_issues = list(repo.get_issues(state="all"))
issues_by_usr = defaultdict(list)
total_issue_comments_by_usr = defaultdict(int)
for i, issue in enumerate(all_issues):
    if issue.pull_request:
        continue

    print(f"Fetched {i}/{len(all_issues)} issues")
    comments = list(issue.get_comments())
    issues_by_usr[issue.user].append(issue)
    users = set()
    for comment in comments:
        if comment.user != issue.user and comment.user not in users:
            total_issue_comments_by_usr[comment.user] += 1
            users.add(comment.user)

print(f"\n\n")
print(f"===========")
print(f"Issue marks")
print(f"===========")
for (user, user_issues) in issues_by_usr.items():
    print(f"\n")
    print(f"============")
    print(f"User: {user.login}")
    print(f"Total number of issues: {len(user_issues)}")
    for i, user_issue in enumerate(user_issues[:MAX_ISSUES_TO_DISPLAY]):
        print(f"\t{i}. {user_issue.title}")
        print(f"\t\t{user_issue.body}")
    if len(user_issues) > MAX_ISSUES_TO_DISPLAY:
        print("... cutting off remaining issues")

#################
## PR scraping ##
#################
print(f"Scraping PR data...")
all_prs = list(repo.get_pulls(state="all"))
prs_by_usr = defaultdict(list)
total_pr_comments_by_usr = defaultdict(int)
for i, pr in enumerate(all_prs):
    print(f"Fetched {i}/{len(all_prs)} PRs")
    prs_by_usr[pr.user].append(pr)

    reviews = list(pr.get_reviews())
    reviewers = set()
    for review in reviews:
        if review.user != pr.user and review.user not in reviewers:
            total_pr_comments_by_usr[review.user] += 1
            reviewers.add(review.user)

print(f"\n\n")
print(f"===================")
print(f"Pull requests marks")
print(f"===================")
for (user, user_prs) in prs_by_usr.items():
    print(f"\n")
    print(f"============")
    print(f"User: {user.login}")
    print(f"Total number: {len(user_prs)}")
    for i, user_pr in enumerate(user_prs[:MAX_PRS_TO_DISPLAY]):
        print(f"\t{i}. {user_pr.title}")
    if len(user_prs) > MAX_PRS_TO_DISPLAY:
        print("... cutting off remaining PRs")

print(f"\n\n")
print(f"========")
print(f"Teamwork")
print(f"========")
print("Number of other people's issues commented on:")
for (user, count) in total_issue_comments_by_usr.items():
    print(f"\t {user.login}: {count}")
print("Number of other people's PRs reviewed")
for (user, count) in total_pr_comments_by_usr.items():
    print(f"\t {user.login}: {count}")
