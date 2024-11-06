import os
import requests


# Get the GitHub token from the environment variable
TOKEN = os.getenv("GITHUB_API_TOKEN")
ORG_NAME = "EnAccess"
GITHUB_API_URL = "https://api.github.com"

if not TOKEN:
    raise ValueError(
        "No GitHub token found. Please set the GITHUB_API_TOKEN environment variable."
    )


# Initialize headers for authentication
headers = {"Authorization": f"token {TOKEN}"}


def get_repos_with_topic(org_name, topic="hacktoberfest"):
    """Fetches all repositories in an organization with a specific topic."""
    repos_with_topic = []
    page = 1
    while True:
        url = f"{GITHUB_API_URL}/orgs/{org_name}/repos?page={page}&per_page=100"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("Failed to fetch repositories:", response.json())
            break
        page_repos = response.json()
        if not page_repos:
            break
        for repo in page_repos:
            if topic in repo.get("topics", []):
                repos_with_topic.append(repo)
        page += 1
    return repos_with_topic


def get_hacktoberfest_prs(repo_full_name):
    """Fetches all merged pull requests in October 2024."""
    prs = []
    page = 1
    while True:
        url = f"{GITHUB_API_URL}/repos/{repo_full_name}/pulls"
        params = {
            "state": "closed",
            "sort": "created",
            "direction": "asc",
            "page": page,
            "per_page": 100,
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print("Failed to fetch pull requests:", response.json())
            break
        page_prs = response.json()
        if not page_prs:
            break
        for pr in page_prs:
            if pr["merged_at"] and "2024-10-01" <= pr["merged_at"][:10] <= "2024-10-31":
                prs.append(pr)
        page += 1
    return prs


def main():
    repos = get_repos_with_topic(ORG_NAME)
    total_prs = 0
    unique_contributors = set()
    new_contributors = set()

    for repo in repos:
        repo_name = repo["full_name"]
        hacktoberfest_prs = get_hacktoberfest_prs(repo_name)

        total_prs += len(hacktoberfest_prs)
        for pr in hacktoberfest_prs:
            contributor = pr["user"]["login"]
            unique_contributors.add(contributor)

            # Check if contributor has prior contributions to the repo
            contrib_url = f"{GITHUB_API_URL}/repos/{repo_name}/contributors"
            contributors_response = requests.get(contrib_url, headers=headers)
            contributors = contributors_response.json()
            if contributor not in [user["login"] for user in contributors]:
                new_contributors.add(contributor)

    print("Total Merged PRs in Hacktoberfest Repos:", total_prs)
    print("Distinct Contributors:", len(unique_contributors))
    print("New Contributors:", len(new_contributors))
    print("\nList of Distinct Contributors:", list(unique_contributors))
    print("\nList of New Contributors:", list(new_contributors))


if __name__ == "__main__":
    main()
