import re
import requests
import sys
from datetime import datetime

# Get GitHub repo details from command line arguments
REPO_OWNER = sys.argv[1]
REPO_NAME = sys.argv[2]
GITHUB_API_URL = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits'

# Define commit types and scopes
TYPES = ["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore"]
SCOPES = ["frontend", "backend", "api", "ui", "docs", "db", "server"]

# Generate type and scope regex dynamically
TYPE_REGEX = '|'.join(TYPES)  # Combine types with `|`
SCOPE_REGEX = '|'.join(SCOPES)  # Combine scopes with `|`

# Short description regex (matches a single line after the colon)
SHORT_DESC_REGEX = ".*"  # Matches the short description after the colon

# Multiline description regex (matches additional lines, including spaces or newlines)
MULTILINE_DESC_REGEX = "[\\s\\S]+"  # Matches multiline description if any

# Refs regex (matches the "Refs: #[A-Za-z0-9-]+" line)
REFS_REGEX = "Refs: #[A-Za-z0-9-]+"  # Refs line regex

# Combine all regex components into a single commit message pattern
COMMIT_MSG_PATTERN = rf"^({TYPE_REGEX})\(({SCOPE_REGEX})\):\s*({SHORT_DESC_REGEX})(\s*({MULTILINE_DESC_REGEX}))?\s*({REFS_REGEX})?$"

# Fetch commits from GitHub
def fetch_commits():
    commits = []
    page = 1
    while True:
        response = requests.get(GITHUB_API_URL, params={'page': page, 'per_page': 100})
        if response.status_code != 200:
            print("Failed to fetch commits")
            break
        data = response.json()
        if not data:
            break
        commits.extend(data)
        page += 1
    return commits

# Parse commits and classify them based on types
def parse_commits(commits):
    classified_commits = {type_: [] for type_ in TYPES}
    for commit in commits:
        message = commit['commit']['message']
        author = commit['commit']['author']['name']
        date = commit['commit']['author']['date']
        match = re.match(COMMIT_MSG_PATTERN, message)
        if match:
            commit_type = match.group(1)
            commit_scope = match.group(2)  # Capture the scope from the commit message
            short_desc = match.group(3)
            classified_commits[commit_type].append({
                'author': author,
                'date': date,
                'message': message,
                'scope': commit_scope,  # Include scope in the output
                'short_desc': short_desc
            })
    return classified_commits

# Generate the commit log document
def generate_commit_log(classified_commits):
    doc_content = f"Commit Log\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    for commit_type, commits in classified_commits.items():
        if commits:  # Only include types with commits
            doc_content += f"\n### {commit_type.capitalize()} Commits:\n"
            for commit in commits:
                doc_content += f" - **{commit['short_desc']}** (Scope: {commit['scope']}, Author: {commit['author']}, Date: {commit['date']})\n"
                doc_content += f"   {commit['message']}\n\n"
    return doc_content

# Save the generated document to a file
def save_commit_log(doc_content, filename="commit_log.md"):
    with open(filename, 'w') as f:
        f.write(doc_content)

def main():
    # Fetch commits from GitHub
    commits = fetch_commits()
    
    # Parse and classify commits
    classified_commits = parse_commits(commits)
    
    # Generate the commit log document
    commit_log = generate_commit_log(classified_commits)
    
    # Save the commit log to a file
    save_commit_log(commit_log)

    print("Commit log has been generated and saved.")

if __name__ == "__main__":
    main()