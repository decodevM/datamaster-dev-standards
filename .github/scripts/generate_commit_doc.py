# import os
# import re
# import requests
# from datetime import datetime
# from typing import Dict, List, Optional
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class CommitParser:
#     def __init__(self):
#         self.TYPES = ["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore"]
#         self.commit_pattern = self._create_commit_pattern()

#     def _create_commit_pattern(self):
#         type_regex = "|".join(self.TYPES)
#         return re.compile(
#             rf"^(?P<type>{type_regex})"
#             r"\((?P<scope>[^)]+)\):\s*"
#             r"(?P<title>[^\n]+)$",
#             re.DOTALL,
#         )

#     def parse(self, message: str) -> Optional[Dict]:
#         match = self.commit_pattern.match(message.strip())
#         if match:
#             return match.groupdict()
#         return None


# class ChangelogGenerator:
#     def __init__(self):
#         self.parser = CommitParser()
#         self.github_token = os.getenv("GITHUB_TOKEN")
#         self.repo_owner = os.getenv("REPO_OWNER")
#         self.repo_name = os.getenv("REPO_NAME")

#     def fetch_commits(self, branch="main") -> List[Dict]:
#         url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/commits"
#         headers = {
#             "Authorization": f"token {self.github_token}",
#             "Accept": "application/vnd.github.v3+json",
#         }

#         commits = []
#         page = 1
#         while True:
#             response = requests.get(
#                 url, headers=headers, params={"sha": branch, "page": page, "per_page": 100}
#             )
#             if response.status_code != 200:
#                 logger.error(f"Failed to fetch commits: {response.json()}")
#                 break

#             data = response.json()
#             if not data:
#                 break

#             commits.extend(data)
#             page += 1

#         return commits

#     def categorize_commits(self, commits: List[Dict]) -> Dict[str, Dict[str, List[str]]]:
#         categorized = {t: {} for t in self.parser.TYPES}
#         seen_commits = set()  # Use a set to track unique commits

#         for commit in commits:
#             message = commit["commit"]["message"]
#             parsed = self.parser.parse(message)
#             if parsed:
#                 # Create a unique identifier for each commit
#                 unique_identifier = f"{parsed['type']}::{parsed['scope']}::{parsed['title']}"
                
#                 if unique_identifier in seen_commits:
#                     continue  # Skip duplicate commits
                
#                 seen_commits.add(unique_identifier)  # Mark as seen
                
#                 commit_type = parsed["type"]
#                 scope = parsed["scope"]
#                 title = parsed["title"]

#                 if scope not in categorized[commit_type]:
#                     categorized[commit_type][scope] = []
#                 categorized[commit_type][scope].append(title)

#         return categorized

#     def generate_markdown(self, categorized_commits: Dict[str, Dict[str, List[str]]]) -> str:
#         emojis = {
#             "feat": "✨",
#             "fix": "🐛",
#             "docs": "📚",
#             "style": "💎",
#             "refactor": "♻️",
#             "perf": "⚡️",
#             "test": "🧪",
#             "chore": "🔧",
#         }

#         today = datetime.now().strftime("%d %B %Y")
#         changelog = [f"# Changelog\n\nGenerated on {today}\n"]

#         for commit_type, scopes in categorized_commits.items():
#             if not scopes:
#                 continue

#             emoji = emojis.get(commit_type, "📌")
#             changelog.append(f"## {emoji} {commit_type.capitalize()}s\n")

#             for scope, titles in scopes.items():
#                 changelog.append(f"### `{scope}`\n")
#                 for title in titles:
#                     changelog.append(f"- {title}")

#         return "\n".join(changelog)

#     def generate_full_markdown(self, commits: List[Dict]) -> str:
#         today = datetime.now().strftime("%d %B %Y")
#         full_changelog = [f"# Full Changelog\n\nGenerated on {today}\n"]
#         emojis = {
#             "feat": "✨",
#             "fix": "🐛",
#             "docs": "📚",
#             "style": "💎",
#             "refactor": "♻️",
#             "perf": "⚡️",
#             "test": "🧪",
#             "chore": "🔧",
#         }
        
#         # Group commits by type
#         categorized_commits = {t: {} for t in self.parser.TYPES}
#         for commit in commits:
#             message = commit["commit"]["message"]
#             parsed = self.parser.parse(message)
#             if parsed:
#                 commit_type = parsed["type"]
#                 scope = parsed["scope"]
#                 title = parsed["title"]
#                 body = commit["commit"].get("body", "")  # Get the commit body
#                 refs = commit["commit"].get("refs", "")  # Get the refs

#                 if scope not in categorized_commits[commit_type]:
#                     categorized_commits[commit_type][scope] = []

#                 # Store the commit with title, body, and refs in the categorized_commits
#                 categorized_commits[commit_type][scope].append({
#                     "title": title,
#                     "body": body,
#                     "refs": refs,
#                 })

#         # Format categorized commits
#         for commit_type, scopes in categorized_commits.items():
#             if not scopes:
#                 continue

#             emoji = emojis.get(commit_type, "📌")
#             full_changelog.append(f"## {emoji} {commit_type.capitalize()}s\n")

#             for scope, commit_list in scopes.items():
#                 full_changelog.append(f"### `{scope}`\n")
#                 for commit in commit_list:
#                     full_changelog.append(f"- **{commit['title']}**")  # Display title
#                     if commit['body']:  # Only display body if it's not empty
#                         full_changelog.append(f"  - Description: {commit['body']}")
#                     if commit['refs']:  # Only display refs if they exist
#                         full_changelog.append(f"  - Refs: {commit['refs']}")

#         return "\n".join(full_changelog)

#     def extract_refs(self, message: str) -> List[str]:
#         """
#         Extract references like issue numbers or PR links from the commit message.
#         Example:
#         - 'Fixes #123'
#         - 'Refs #456'
#         """
#         refs = re.findall(r"(#\d+)", message)  # Find all occurrences of # followed by numbers
#         return refs

#     def save_changelog(self, content: str, filename="generated_docs/CHANGELOG.md"):
#         os.makedirs(os.path.dirname(filename), exist_ok=True)  # Ensure the directory exists
#         with open(filename, "w", encoding="utf-8") as f:
#             f.write(content)
#         logger.info(f"Changelog saved to {filename}")


# def main():
#     # Ensure required environment variables are set
#     for env_var in ["GITHUB_TOKEN", "REPO_OWNER", "REPO_NAME"]:
#         if not os.getenv(env_var):
#             logger.error(f"Environment variable {env_var} is missing!")
#             return

#     branch = os.getenv("BRANCH", "main")

#     generator = ChangelogGenerator()
#     commits = generator.fetch_commits(branch=branch)

#     if not commits:
#         logger.error("No commits found. Exiting.")
#         return

#     categorized_commits = generator.categorize_commits(commits)
#     release_changelog = generator.generate_markdown(categorized_commits)
#     generator.save_changelog(release_changelog, "generated_docs/RELEASE_CHANGELOG.md")

#     full_changelog = generator.generate_full_markdown(commits)
#     generator.save_changelog(full_changelog, "generated_docs/FULL_CHANGELOG.md")


# if __name__ == "__main__":
#     main()


#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------




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
            r"(?P<title>[^\n]+)\n"  # Title line
            r"(?P<body>(?:.|\n)*?)"  # Body (can be empty)
            r"(?:\n(?P<footer>.+))?$",  # Footer (can be empty)
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
                body = parsed.get("body", "").strip()
                footer = parsed.get("footer", "").strip()

                if scope not in categorized[commit_type]:
                    categorized[commit_type][scope] = []
                categorized[commit_type][scope].append({
                    "title": title,
                    "body": body,
                    "footer": footer,
                })

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

            for scope, commit_list in scopes.items():
                changelog.append(f"### `{scope}`\n")
                for commit in commit_list:
                    changelog.append(f"- **{commit['title']}**")  # Display title
                    if commit['body']:  # Only display body if it's not empty
                        changelog.append(f"  - Description: {commit['body']}")
                    if commit['footer']:  # Only display footer if it exists
                        changelog.append(f"  - Footer: {commit['footer']}")

        return "\n".join(changelog)

    def generate_full_markdown(self, commits: List[Dict]) -> str:
        today = datetime.now().strftime("%d %B %Y")
        full_changelog = [f"# Full Changelog\n\nGenerated on {today}\n"]
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

        # Group commits by type
        categorized_commits = {t: {} for t in self.parser.TYPES}
        for commit in commits:
            message = commit["commit"]["message"]
            parsed = self.parser.parse(message)
            if parsed:
                commit_type = parsed["type"]
                scope = parsed["scope"]
                title = parsed["title"]
                body = parsed.get("body", "")  # Get the commit body
                footer = parsed.get("footer", "")  # Get the commit footer

                if scope not in categorized_commits[commit_type]:
                    categorized_commits[commit_type][scope] = []

                # Store the commit with title, body, and footer in the categorized_commits
                categorized_commits[commit_type][scope].append({
                    "title": title,
                    "body": body,
                    "footer": footer,
                })

        # Format categorized commits
        for commit_type, scopes in categorized_commits.items():
            if not scopes:
                continue

            emoji = emojis.get(commit_type, "📌")
            full_changelog.append(f"## {emoji} {commit_type.capitalize()}s\n")

            for scope, commit_list in scopes.items():
                full_changelog.append(f"### `{scope}`\n")
                for commit in commit_list:
                    full_changelog.append(f"- **{commit['title']}**")  # Display title
                    if commit['body']:  # Only display body if it's not empty
                        full_changelog.append(f"  - Description: {commit['body']}")
                    if commit['footer']:  # Only display footer if it exists
                        full_changelog.append(f"  - Footer: {commit['footer']}")

        return "\n".join(full_changelog)

    def save_changelog(self, content: str, filename="generated_docs/CHANGELOG.md"):
        os.makedirs(os.path.dirname(filename), exist_ok=True)  # Ensure the directory exists
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
    release_changelog = generator.generate_markdown(categorized_commits)
    generator.save_changelog(release_changelog, "generated_docs/RELEASE_CHANGELOG.md")

    full_changelog = generator.generate_full_markdown(commits)
    generator.save_changelog(full_changelog, "generated_docs/FULL_CHANGELOG.md")


if __name__ == "__main__":
    main()