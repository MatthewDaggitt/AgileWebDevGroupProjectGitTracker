from collections import defaultdict
from github import Github
from github import Auth
import os
import sys
from rich.table import Table
from rich.console import Console
from rich import box
from tqdm import tqdm

MAX_COMMITS_TO_DISPLAY = 50
MAX_ISSUES_TO_DISPLAY = 50
MAX_PRS_TO_DISPLAY = 50

PRINT_LOGS = False

TOKEN = os.environ.get("GITHUB_ACCESS_TOKEN")

auth = Auth.Token(TOKEN)

repo_url = sys.argv[1]


g = Github(auth=auth)
limit = g.get_rate_limit().core
print(f"Hourly queries: {limit.limit}")
print(f"Queries remaining: {limit.remaining}")

print(f"Repo URL: {repo_url}")
repo = g.get_repo(repo_url)

console = Console()

#####################
## Commit scraping ##
#####################
commit_table = Table(title="Commits per User", show_lines=True)
commit_table.add_column("User")
commit_table.add_column("Commits", justify="right")
commit_table.add_column("Messages")

print(f"Scraping commit data...")
all_commits = repo.get_commits()
commits_by_usr = defaultdict(list)
for commit in all_commits:
    if commit.author:
        commits_by_usr[commit.author.login].append(commit)
    elif commit.commit.author:
        # For people who have not configured their GitHub users correctly
        commits_by_usr[commit.commit.author.name].append(commit)

print(f"\n\n")
print(f"============")
print(f"Commit marks")
print(f"============")

for user, user_commits in commits_by_usr.items():
    if PRINT_LOGS:
        print(f"\n")
        print(f"============")
        print(f"User: {user}")
        print(f"Total number: {len(user_commits)}")
    percent = (len(user_commits) / all_commits.totalCount) * 100
    messages = ""
    for id, user_commit in enumerate(user_commits[:MAX_COMMITS_TO_DISPLAY]):
        message = user_commit.commit.message
        if PRINT_LOGS: print(f"{id}. {message}")
        messages += f"{id+1} - {message}\n"
    if len(user_commits) > MAX_COMMITS_TO_DISPLAY:
        message = "... cutting off remaining commits"
        if PRINT_LOGS: print(message)
        messages += message
    commit_table.add_row(user, f"{len(user_commits)} ({percent:.1f}%)", messages)


console.print(commit_table)


####################
## Issue scraping ##
####################
issue_table = Table(title="Issues per User", show_lines=True)
issue_table.add_column("User")
issue_table.add_column("Issues", justify="right")
issue_table.add_column("Title", justify="left")
issue_table.add_column("Comments", justify="left")

print(f"\n\n")
print(f"Scraping issue data...")
all_issues = list(repo.get_issues(state="all"))
issues_by_usr = defaultdict(list)
total_issue_comments_by_usr = defaultdict(int)

for i, issue in enumerate(tqdm(all_issues, desc="Fetching issues")):
    if issue.pull_request:
        continue

    # print(f"Fetched {i}/{len(all_issues)} issues")
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
previous_user = None
for user, user_issues in issues_by_usr.items():
    if PRINT_LOGS:
        print(f"\n")
        print(f"============")
        print(f"User: {user.login}")
        print(f"Total number of issues: {len(user_issues)}")

    for i, user_issue in enumerate(user_issues[:MAX_ISSUES_TO_DISPLAY]):
        issue_title = user_issue.title
        issue_comment = f"\t\t{user_issue.body}".replace("\n", "\n\t\t")
        if PRINT_LOGS:
            print(f"\t{i}. {issue_title}")
            print(issue_comment)
        if previous_user != user.login:
            issue_table.add_row(user.login, str(len(user_issues)), f"{i+1}-{issue_title.strip()}", issue_comment.strip())
        else:
            issue_table.add_row("", "", f"{i+1}-{issue_title.strip()}", issue_comment.strip())
        previous_user = user.login
    if len(user_issues) > MAX_ISSUES_TO_DISPLAY:
        message = "... cutting off remaining issues"
        if PRINT_LOGS: print(message)
        issue_table.add_row("", "", "", message)

console.print(issue_table)

#################
## PR scraping ##
#################
pr_table = Table(title="PRs per User", show_lines=True)
pr_table.add_column("User")
pr_table.add_column("PRs", justify="left")
pr_table.add_column("Title", justify="left")


print(f"Scraping PR data...")
all_prs = list(repo.get_pulls(state="all"))
prs_by_usr = defaultdict(list)
total_pr_comments_by_usr = defaultdict(int)
for i, pr in enumerate(tqdm(all_prs, desc="Fetching PRs")):
    # print(f"Fetched {i}/{len(all_prs)} PRs")
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
for user, user_prs in prs_by_usr.items():
    if PRINT_LOGS: print(f"\n")
    if PRINT_LOGS: print(f"============")
    if PRINT_LOGS: print(f"User: {user.login}")
    if PRINT_LOGS: print(f"Total number: {len(user_prs)}")
    user_messages = ""
    for i, user_pr in enumerate(user_prs[:MAX_PRS_TO_DISPLAY]):
        if PRINT_LOGS: print(f"\t{i}. {user_pr.title}")
        user_messages += f"{i+1} - {user_pr.title}\n"
    if len(user_prs) > MAX_PRS_TO_DISPLAY:
        if PRINT_LOGS: print("... cutting off remaining PRs")
        user_messages += "... cutting off remaining PRs\n"
    pr_table.add_row(user.login, str(len(user_prs)), user_messages.strip())

console.print(pr_table)


print(f"\n\n")
print(f"========")
print(f"Teamwork")
print(f"========")

team_work_table = Table(title="Teamwork", show_lines=False)
team_work_table.add_column("User")
team_work_table.add_column("Number of other people's issue commented on", justify="left")
team_work_table.add_column("Number of other people's PR reviewed", justify="left")

all_users = set(list(total_pr_comments_by_usr.keys()) + list(total_issue_comments_by_usr))
for user in all_users:
    team_work_table.add_row(user.login, str(total_issue_comments_by_usr[user]), str(total_pr_comments_by_usr[user]))

if PRINT_LOGS: print("Number of other people's issues commented on:")
for user, count in total_issue_comments_by_usr.items():
    if PRINT_LOGS: print(f"\t {user.login}: {count}")

if PRINT_LOGS: print("Number of other people's PRs reviewed")
for user, count in total_pr_comments_by_usr.items():
    if PRINT_LOGS: print(f"\t {user.login}: {count}")

console.print(team_work_table)
