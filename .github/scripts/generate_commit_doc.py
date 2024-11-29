import os
import requests
from datetime import datetime
import re

# Constants
COMMIT_TYPES = ["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore"]
GITHUB_API_URL = "https://api.github.com"

# Environment variables
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_OWNER = os.getenv('REPO_OWNER')
REPO_NAME = os.getenv('REPO_NAME')

class CommitDocument:
    def __init__(self):
        self.commit_pattern = self._create_commit_pattern()
        
    def _create_commit_pattern(self):
        type_regex = "|".join(COMMIT_TYPES)
        return f"^({type_regex})\\((.*?)\\):\\s*(.*?)(\\n[\\s\\S]*)?$"

    def fetch_commits(self, branch="main"):
        url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/commits"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        commits = []
        page = 1
        
        while True:
            response = requests.get(
                url, 
                headers=headers,
                params={"sha": branch, "page": page}
            )
            
            if response.status_code != 200:
                print(f"Error fetching commits: {response.status_code}")
                break
                
            data = response.json()
            if not data:
                break
                
            commits.extend(data)
            page += 1
            
        return commits

    def parse_commit_message(self, message):
        match = re.match(self.commit_pattern, message, re.MULTILINE)
        if not match:
            return None
            
        commit_type, scope, title, body = match.groups()
        # Remove the "Required scripts are:" section and everything after it
        if body:
            body = body.split("Required scripts are:")[0].strip()
            
        return {
            "type": commit_type,
            "scope": scope or "general",
            "title": title.strip(),
            "body": body
        }

    def categorize_commits(self, commits):
        categorized = {t: [] for t in COMMIT_TYPES}
        
        for commit in commits:
            message = commit["commit"]["message"]
            author = commit["commit"]["author"]["name"]
            date = commit["commit"]["author"]["date"]
            
            parsed = self.parse_commit_message(message)
            if parsed:
                commit_info = {
                    "scope": parsed["scope"],
                    "title": parsed["title"],
                    "description": parsed["body"],
                    "date": date,
                    "author": author
                }
                categorized[parsed["type"]].append(commit_info)
                
        return categorized

    def generate_markdown(self, categorized_commits):
        today = datetime.now().strftime("%d %B %Y")
        
        doc = [
            "# Rapport des Commits",
            f"Generated on {today}\n",
            "## Client: Project Name\n",
            "## Commit Details"
        ]
        
        for commit_type in COMMIT_TYPES:
            commits = categorized_commits[commit_type]
            if not commits:
                continue
                
            doc.append(f"### {commit_type.capitalize()}s")
            
            for idx, commit in enumerate(commits, 1):
                doc.extend([
                    f"{commit_type.capitalize()} {idx}: ({commit['scope']}) {commit['title']}",
                    f"    Description: {commit['description']}" if commit['description'] else "",
                    f"    Date: {commit['date']}",
                    f"    Author: {commit['author']}\n"
                ])
                
        return "\n".join(filter(None, doc))

    def generate_full_markdown(self, commits):
        today = datetime.now().strftime("%d %B %Y")
        full_changelog = [f"# Full Changelog\n\nGenerated on {today}\n"]

        for commit in commits:
            author = commit["commit"]["author"]["name"]
            message = commit["commit"]["message"]
            sha = commit["sha"]
            full_changelog.append(f"## {author} - {sha}\n")
            full_changelog.append(f"- {message}\n")

        return "\n".join(full_changelog)

    def save_document(self, content, filename="generated_docs/commit_document.md"):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            f.write(content)
        print(f"Document saved to: {filename}")


def main():
    doc_generator = CommitDocument()
    
    # Fetch and process commits
    commits = doc_generator.fetch_commits()
    if not commits:
        print("No commits found")
        return
        
    # Categorize commits and generate documents
    categorized_commits = doc_generator.categorize_commits(commits)
    markdown = doc_generator.generate_markdown(categorized_commits)
    
    # Save categorized changelog
    doc_generator.save_document(markdown, "generated_docs/commit_changelog.md")
    
    # Generate and save full changelog
    full_changelog = doc_generator.generate_full_markdown(commits)
    doc_generator.save_document(full_changelog, "generated_docs/full_changelog.md")
    
    print("Commit documents generated successfully!")


if __name__ == "__main__":
    main()