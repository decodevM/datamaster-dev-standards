import os
import re
from datetime import datetime
import requests
from typing import Dict, Optional, List
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CommitParser:
    def __init__(self):
        self.TYPES = ["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore"]
        self.commit_pattern = self._create_commit_pattern()

    def _create_commit_pattern(self):
        type_regex = "|".join(self.TYPES)
        return re.compile(
            r"^(?P<type>" + type_regex + ")"
            r"\((?P<scope>[^)]+)\):\s*"
            r"(?P<title>[^\n]+)"
            r"(?:(?P<body>[\s\S]*?))?"  # Non-greedy match for the body
            r"(?:\nRefs:\s*(?P<refs>#[A-Za-z0-9-]+(?:,\s*#[A-Za-z0-9-]+)*))?"  # Non-greedy match for the footer
            r"$", re.DOTALL
        )

    def parse(self, message: str) -> Optional[Dict]:
        try:
            if not message or not isinstance(message, str):
                logger.warning(f"Invalid message format: {message}")
                return None

            message = message.strip()
            match = self.commit_pattern.match(message)
            
            if not match:
                logger.debug(f"No match found for message: {message}")
                return None

            result = match.groupdict()
            
            # Safe string operations with null checks
            return {
                "type": result.get("type", ""),
                "scope": result.get("scope", ""),
                "title": result.get("title", ""),
                "body": result.get("body", "").strip() if result.get("body") else "",  # Ensure body is stripped
                "refs": [ref.strip() for ref in result.get("refs", "").split(",")] if result.get("refs") else []
            }
            
        except Exception as e:
            logger.error(f"Error parsing commit message: {e}")
            return None

class CommitDocument:
    def __init__(self):
        self.parser = CommitParser()
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_owner = os.getenv('REPO_OWNER')
        self.repo_name = os.getenv('REPO_NAME')

    def fetch_commits(self, branch="main"):
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/commits"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        commits = []
        page = 1
        
        while True:
            try:
                response = requests.get(
                    url, 
                    headers=headers,
                    params={"sha": branch, "page": page}
                )
                response.raise_for_status()
                
                data = response.json()
                if not data:
                    break
                    
                commits.extend(data)
                page += 1
                
            except Exception as e:
                logger.error(f"Error fetching commits: {e}")
        return commits

    def categorize_commits(self, commits):
        categorized = {t: [] for t in self.parser.TYPES}
        
        for commit in commits:
            message = commit["commit"]["message"]
            author = commit["commit"]["author"]["name"]
            date = datetime.strptime(
                commit["commit"]["author"]["date"], 
                "%Y-%m-%dT%H:%M:%SZ"
            ).strftime("%d %B %Y %H:%M")
            
            parsed = self.parser.parse(message)
            if parsed:
                commit_info = {
                    **parsed,
                    "date": date,
                    "author": author
                }
                categorized[parsed["type"]].append(commit_info)
                
        return categorized

    def generate_markdown(self, categorized_commits):
        emojis = {
            "feat": "✨",
            "fix": "🐛",
            "docs": "📚",
            "style": "💎",
            "refactor": "♻️",
            "perf": "⚡️",
            "test": "🧪",
            "chore": "🔧"
        }
        
        today = datetime.now().strftime("%d %B %Y")
        
        doc = [
            "# 📄 Commit Report",
            f"*Generated on {today}*\n",
            "## 🏢 Project Commits\n"
        ]
        
        for commit_type in self.parser.TYPES:
            commits = categorized_commits[commit_type]
            if not commits:
                continue
                
            emoji = emojis.get(commit_type, "📌")
            doc.append(f"### {emoji} {commit_type.capitalize()}s\n")
            
            for commit in commits:
                doc.extend([
                    f"#### `{commit['scope']}` {commit['title']}",
                    f"*{commit['author']} - {commit['date']}*\n",
                    f"{commit['body']}\n" if commit['body'] else "",
                    f"🔗 {', '.join(commit['refs'])}\n" if commit['refs'] else "",
                    "---\n"


                    
                ])
                
        return "\n".join(filter(None, doc))

    def save_document(self, content, filename="generated_docs/commit_document.md"):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Document saved to: {filename}")

def main():
    doc_generator = CommitDocument()
    commits = doc_generator.fetch_commits()
    
    if not commits:
        print("❌ No commits found")
        return
        
    categorized = doc_generator.categorize_commits(commits)
    markdown = doc_generator.generate_markdown(categorized)
    doc_generator.save_document(markdown)

if __name__ == "__main__":
    main()