import os
import requests
import re
from datetime import datetime

# Predefined commit types
TYPES = ["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore"]

# Define the commit message pattern based on your format
TYPE_REGEX = "|".join(TYPES)
SHORT_DESC_REGEX = ".*"
MULTILINE_DESC_REGEX = "[\\s\\S]+"  # Multiline description
REFS_REGEX = "Refs: #[A-Za-z0-9-]+"

# Commit message pattern to match
COMMIT_MSG_PATTERN = f"^({TYPE_REGEX})\\((.*?)\\):\\s*({SHORT_DESC_REGEX})(\\s*{MULTILINE_DESC_REGEX})?\\s*({REFS_REGEX})?$"

# GitHub API details
GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # Make sure GITHUB_TOKEN is set in GitHub secrets
REPO_OWNER = os.getenv('GITHUB_REPOSITORY').split('/')[0]  # Get owner from the environment variable
REPO_NAME = os.getenv('GITHUB_REPOSITORY').split('/')[1]    # Get repo name from the environment variable

# Function to get commits from the repository
def get_commits(owner, repo, branch="main"):
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/commits?sha={branch}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    commits = []
    page = 1
    while True:
        response = requests.get(url + f"&page={page}", headers=headers)
        if response.status_code != 200:
            print(f"Error fetching commits: {response.status_code}")
            break
        data = response.json()
        if not data:
            break
        commits.extend(data)
        page += 1
    return commits

# Function to categorize commits based on commit message pattern
def categorize_commits(commits):
    categorized_commits = {commit_type: [] for commit_type in TYPES}
    for commit in commits:
        message = commit["commit"]["message"]
        author = commit["commit"]["author"]["name"]
        date = commit["commit"]["author"]["date"]
        sha = commit["sha"]
        
        # Check if the commit message matches the pattern
        match = re.match(COMMIT_MSG_PATTERN, message)
        if match:
            commit_type = match.group(1)
            scope = match.group(2)  # Dynamically capture the scope from the commit message
            short_description = match.group(3)
            # Optionally handle the multiline description and refs
            multiline_description = match.group(4) or ""
            refs = match.group(5) or ""

            # Prepare the commit message
            commit_message = f"**Message:** {message}\n**Date:** {date}\n**Author:** {author}\n**SHA:** {sha}\n{multiline_description}\n{refs}"

            # Append the commit message to the corresponding type array
            categorized_commits[commit_type].append({"scope": scope, "message": commit_message})
    
    return categorized_commits

# Function to generate the commit log document in Markdown format
def generate_commit_log(categorized_commits):
    today_date = datetime.now().strftime("%d %B %Y")
    client_name = "Client Name"  # Change to the client name if needed

    commit_log = f"# Rapport des Commits\n" \
                 f"Generated on {today_date}\n\n" \
                 f"## Client: {client_name}\n\n" \
                 f"## Commit Details\n"

    for commit_type in TYPES:
        if categorized_commits[commit_type]:
            commit_log += f"### {commit_type.capitalize()}s\n"
            for idx, commit in enumerate(categorized_commits[commit_type], start=1):
                commit_log += f"#### {commit_type.capitalize()} {idx}: {commit['message']}\n\n"
    
    return commit_log

# Function to save the commit log to a Markdown file
def save_commit_log(doc_content, filename="generated_docs/commit_document.md"):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w') as f:
        f.write(doc_content)

# Main function to fetch commits, categorize them, and generate the log
def main():
    commits = get_commits(REPO_OWNER, REPO_NAME)
    categorized_commits = categorize_commits(commits)
    commit_log = generate_commit_log(categorized_commits)
    save_commit_log(commit_log)
    print("Commit log generated successfully as Markdown!")

# Run the script
if __name__ == "__main__":
    main()