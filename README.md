# AgileWebDevGroupProjectGitTracker

A script for scraping GitHub information for marrking the Group Project for Agile Web Dev at UWA

Installation instructions

1. Setup and activate a virtual environment
    ```python
    python -m venv venv
    source venv/bin/activate
    ```

2. Run `pip install -r requirements.txt`

3. Setup a GitHub personal access token (https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)

4. Set the environment variable `GITHUB_ACCESS_TOKEN` to the token (e.g. `export GITHUB_ACCESS_TOKEN="github_pat_11AAP26EQ0ka17r0f1nu3L_cGkBI9eF5tO8ct8og4nVBcJLQXw1PqHdQeS8yDwt7VPG7ROV3GJvc7pAJ"`)

5. There are two scripts that you can run...
    - **Single repository** - `python run.py X\Y` where `X` is the name of the user that owns the repo, and `Y` is the name of the repo.
    - **Batch scrape** - In `batch_scrape.py`, replace `GITHUB_REPOS` with the list of repositories (full link) you want to scrape and run `python batch_scrape.py`
      - Optionally change the `MAX_WORKERS` to the number of threads you want to use for scraping