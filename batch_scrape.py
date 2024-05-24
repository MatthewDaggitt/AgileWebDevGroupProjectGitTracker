"""
batch-scrape all the github repos and write them to a file
"""

import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

# Number of threads to use
MAX_WORKERS = 20

# Just copy the rows and encase in quotes, in same order they appear in spreadsheet
GITHUB_REPOS = [
    "https://github.com/MonkeInABox/CITS3403Project",
    "https://github.com/HarryRMorrison/CareerKickstart",
    "https://github.com/imran072/request-forum-app",
    "https://github.com/harshchaudh/cits3403-project",
    "https://github.com/CelynChew/ChatSome",
    "https://github.com/Semuca/CITS3403",
    "https://github.com/Jalil32/awd-3403",
    "https://github.com/hernancx09/UWA_CITS_3402_Project",
    "https://github.com/IsoVictor/CITS3403-Group-Project",
    "https://github.com/justinarat/cits3403-project",
    "https://github.com/yunho7687/quest-quay",
    "https://github.com/miacheng2/CITS5505-Project2",
    "https://github.com/Lingwan-Peng/CITS3403-Project.git",
    "https://github.com/Misoto22/Paw-Forum",
    "https://github.com/onlinepatron/CampusBookShelf.git",
    "https://github.com/CITS5505GroupProject/CITS5505-Group-Project",
    "https://github.com/Sungchur/WebPrj2",
    "https://github.com/OllieForrest/GroupProject.git",
    "https://github.com/ramandatta87/CITS5505_UWA_Group_Project.git",
    "https://github.com/AlteredOracle/ForumEdit",
]

script = "run.py"

# make directory
if not os.path.exists("github_scrape"):
    os.makedirs("github_scrape")


def scrape_repo(i, repo):
    print(f"Scraping {repo}...")
    repo = "/".join(repo.split("/")[-2:])
    repo = repo[:-4] if repo.endswith(".git") else repo

    fname = f"github_scrape/{i} - {repo.replace('/', '-')}.txt"
    out = subprocess.run(["python", script, repo], capture_output=True, text=True)

    # Add number to name to sort the files in order they were given in the list
    with open(fname, "w") as f:
        f.write(out.stdout)

    return fname


with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    tasks = [
        executor.submit(scrape_repo, i, repo) for i, repo in enumerate(GITHUB_REPOS, 1)
    ]
    for future in as_completed(tasks):
        try:
            fname = future.result()
            print(f"Finished scraping {fname}")
        except Exception as e:
            print(f"Error: {e}")
