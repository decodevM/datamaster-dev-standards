import os
import re
import requests
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommitParser:
    def __init__(self):
        self.TYPES = ["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore"]
        self.commit_pattern = self._create_commit_pattern()

    def _create_commit_pattern(self):
        type_regex = "|".join(self.TYPES)
        return re.compile(
            rf"^(?P<type>{type_regex})"
            r"\((?P<scope>[^)]+)\):\s*"
            r"(?P<title>[^\n]+)$",
            re.DOTALL,
        )

    def parse(self, message: str) -> Optional[Dict]:
        match = self.commit_pattern.match(message.strip())
        if match:
            return match.groupdict()
        return None


class ChangelogGenerator:
    def __init__(self):
        self.parser = CommitParser()
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo_owner = os.getenv("REPO_OWNER")
        self.repo_name = os.getenv("REPO_NAME")

    def fetch_commits(self, branch="main") -> List[Dict]:
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/commits"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        commits = []
        page = 1
        while True:
            response = requests.get(
                url, headers=headers, params={"sha": branch, "page": page, "per_page": 100}
            )
            if response.status_code != 200:
                logger.error(f"Failed to fetch commits: {response.json()}")
                break

            data = response.json()
            if not data:
                break

            commits.extend(data)
            page += 1

        return commits

    def categorize_commits(self, commits: List[Dict]) -> Dict[str, Dict[str, List[str]]]:
        categorized = {t: {} for t in self.parser.TYPES}
        seen_commits = set()  # Use a set to track unique commits

        for commit in commits:
            message = commit["commit"]["message"]
            parsed = self.parser.parse(message)
            if parsed:
                # Create a unique identifier for each commit
                unique_identifier = f"{parsed['type']}::{parsed['scope']}::{parsed['title']}"
                
                if unique_identifier in seen_commits:
                    continue  # Skip duplicate commits
                
                seen_commits.add(unique_identifier)  # Mark as seen
                
                commit_type = parsed["type"]
                scope = parsed["scope"]
                title = parsed["title"]

                if scope not in categorized[commit_type]:
                    categorized[commit_type][scope] = []
                categorized[commit_type][scope].append(title)

        return categorized

    def generate_markdown(self, categorized_commits: Dict[str, Dict[str, List[str]]]) -> str:
        emojis = {
            "feat": "✨",
            "fix": "🐛",
            "docs": "📚",
            "style": "💎",
            "refactor": "♻️",
            "perf": "⚡️",
            "test": "🧪",
            "chore": "🔧",
        }

        today = datetime.now().strftime("%d %B %Y")
        changelog = [f"# Changelog\n\nGenerated on {today}\n"]

        for commit_type, scopes in categorized_commits.items():
            if not scopes:
                continue

            emoji = emojis.get(commit_type, "📌")
            changelog.append(f"## {emoji} {commit_type.capitalize()}s\n")

            for scope, titles in scopes.items():
                changelog.append(f"### `{scope}`\n")
                for title in titles:
                    changelog.append(f"- {title}")

        return "\n".join(changelog)

    def save_changelog(self, content: str, filename="CHANGELOG.md"):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Changelog saved to {filename}")


def main():
    # Ensure required environment variables are set
    for env_var in ["GITHUB_TOKEN", "REPO_OWNER", "REPO_NAME"]:
        if not os.getenv(env_var):
            logger.error(f"Environment variable {env_var} is missing!")
            return

    branch = os.getenv("BRANCH", "main")

    generator = ChangelogGenerator()
    commits = generator.fetch_commits(branch=branch)

    if not commits:
        logger.error("No commits found. Exiting.")
        return

    categorized_commits = generator.categorize_commits(commits)
    changelog = generator.generate_markdown(categorized_commits)
    generator.save_changelog(changelog)


if __name__ == "__main__":
    main()