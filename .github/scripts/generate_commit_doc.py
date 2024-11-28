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
REPO_OWNER = os.getenv('REPO_OWNER')  # Get owner from the environment variable
REPO_NAME = os.getenv('REPO_NAME')    # Get repo name from the environment variable

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

        # Debugging: print commit message to check if we're fetching the correct data
        print(f"Commit: {message}")
        
        # Check if the commit message matches the pattern
        match = re.match(COMMIT_MSG_PATTERN, message)
        if match:
            # Check if the commit message matches the expected format
            commit_type = match.group(1)
            
            # Check if scope exists, if not, set it to None or some default value
            scope = match.group(2) if match.group(2) else None
            
            # Short description can be directly captured from the third group
            short_description = match.group(3)
            
            # Handle multiline description if any
            multiline_description = match.group(4) if match.group(4) else ""
            
            # Handle refs if present
            refs = match.group(5) if match.group(5) else ""

            # Prepare the commit message
            commit_message = f"**Message:** {message}\n**Date:** {date}\n**Author:** {author}\n**SHA:** {sha}\n{multiline_description}\n{refs}"

            # Append the commit message to the corresponding type array
            categorized_commits[commit_type].append({"scope": scope, "message": commit_message})
        else:
            print(f"Skipped (no match): {message}")  # Debugging: if commit message doesn't match regex

    return categorized_commits

# Function to generate the commit log in the format you requested
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
                # Prepare the commit message according to the new format
                commit_message = commit['message']
                commit_log += f"{commit_type.capitalize()} {idx}: ({commit['scope']})\n"
                commit_log += f"    Description: {commit_message}\n"
                
                if commit['Refs']:  # Check for references
                    commit_log += f"    Refs: {commit['refs']}\n"
                
                commit_log += f"    Date: {commit['date']}\n"
                commit_log += f"    Author: {commit['author']}\n\n"
    
    return commit_log

# Function to save the commit log to a Markdown file
def save_commit_log(doc_content, filename="generated_docs/commit_document.md"):
    # Ensure the directory exists
    dir_name = os.path.dirname(filename)
    if not os.path.exists(dir_name):
        print(f"Creating directory: {dir_name}")
        os.makedirs(dir_name, exist_ok=True)
    
    with open(filename, 'w') as f:
        f.write(doc_content)
    print(f"Commit log saved to: {filename}")

# Main function to fetch commits, categorize them, and generate the log
def main():
    # Fetch commits from the repository
    commits = get_commits(REPO_OWNER, REPO_NAME)
    print(f"Fetched {len(commits)} commits")  # Debugging: check how many commits are fetched
    
    # Categorize the fetched commits
    categorized_commits = categorize_commits(commits)
    
    # Generate commit log in Markdown format
    commit_log = generate_commit_log(categorized_commits)
    
    if not any(categorized_commits.values()):  # Check if no commits were categorized
        print("No commits matched the pattern")
    else:
        # Save the generated commit log to a Markdown file
        save_commit_log(commit_log)
        print("Commit log generated successfully as Markdown!")

# Run the script
if __name__ == "__main__":
    main()