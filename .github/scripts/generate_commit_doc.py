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




import os
import re
import git
from typing import Dict, List, Optional
from datetime import datetime
import logging

# Define the emoji mapping for each commit type
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

# Set up the types as in your shell script (the scopes will be dynamically extracted)
TYPES = ["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore"]

# Dynamically generate regex for type (fixed types as above) and dynamic scope (captured in the parentheses)
TYPE_REGEX = "|".join(TYPES)
SCOPE_REGEX = r"([a-zA-Z0-9-_]+)"  # Capture dynamic scope, alphanumeric, dashes, and underscores

# Regex patterns for short description, multiline description, and refs
SHORT_DESC_REGEX = ".*"  # Matches the short description (commit title)
MULTILINE_DESC_REGEX = "[\\s\\S]+"  # Matches multiline description (commit body)
REFS_REGEX = "Refs: #[A-Za-z0-9-]+"  # Refs line regex

# Combine all regex into a full commit message pattern
COMMIT_MSG_PATTERN = re.compile(
    rf"^({TYPE_REGEX})\(({SCOPE_REGEX})\):\s*({SHORT_DESC_REGEX})(\s*{MULTILINE_DESC_REGEX})?\s*({REFS_REGEX})?$"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommitParser:
    def __init__(self):
        self.commit_pattern = COMMIT_MSG_PATTERN

    def parse(self, message: str) -> Optional[Dict]:
        # Match the commit message to the pattern
        match = self.commit_pattern.match(message.strip())
        if match:
            # Extract the groups into a dictionary
            commit_data = {
                "type": match.group(1),
                "scope": match.group(2),  # Dynamic scope extracted
                "short_description": match.group(3),
                "body": match.group(4) if match.group(4) else None,
                "footer": match.group(5) if match.group(5) else None,
            }
            return commit_data
        return None

class ChangelogGenerator:
    def __init__(self, repo_path: str):
        self.repo = git.Repo(repo_path)
        self.parser = CommitParser()

    def get_commits(self, since_commit: str = "HEAD~10") -> List[Dict]:
        # Fetch commits from the repo
        commits = list(self.repo.iter_commits(since=since_commit))
        parsed_commits = []
        for commit in commits:
            commit_data = self.parser.parse(commit.message)
            if commit_data:
                commit_data["hash"] = commit.hexsha
                commit_data["date"] = commit.committed_datetime
                commit_data["author"] = commit.author.name  # Add commit author's name
                parsed_commits.append(commit_data)
        return parsed_commits

    def generate_full_changelog(self, since_commit: str = "HEAD~10") -> str:
        commits = self.get_commits(since_commit)
        changelog = "# **Full Changelog**\n\n"
        
        for commit in commits:
            changelog += f"### **{emojis.get(commit['type'], '')} {commit['type'].capitalize()}** ({commit['scope']})\n"
            changelog += f"**Commit ID**: `{commit['hash']}`\n"
            changelog += f"**Date**: {commit['date'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            changelog += f"**Author**: {commit['author']}\n"
            changelog += f"**Short Description**: {commit['short_description']}\n"
            
            # Add body if exists
            if commit['body']:
                changelog += f"\n**Body**:\n> {commit['body']}\n"
            
            # Add footer (Refs) if exists
            if commit['footer']:
                changelog += f"\n**Footer (Refs)**: {commit['footer']}\n"
            
            changelog += "\n---\n"
        
        return changelog

    def generate_release_changelog(self, since_commit: str = "HEAD~10") -> str:
        commits = self.get_commits(since_commit)
        changelog = "# **Release Changelog**\n\n"
        
        # Categorize commits by type (feature, fix, docs, etc.)
        changelog_dict = {
            "Features": [],
            "Fixes": [],
            "Docs": [],
            "Others": []
        }

        for commit in commits:
            if commit["type"] == "feat":
                changelog_dict["Features"].append(commit)
            elif commit["type"] == "fix":
                changelog_dict["Fixes"].append(commit)
            elif commit["type"] == "docs":
                changelog_dict["Docs"].append(commit)
            else:
                changelog_dict["Others"].append(commit)

        # Add feature, fix, and docs sections to the changelog
        for section, section_commits in changelog_dict.items():
            if section_commits:
                changelog += f"## **{section}**\n"
                for commit in section_commits:
                    changelog += f"- **{emojis.get(commit['type'], '')} [{commit['short_description']}]**({commit['hash']})\n"
                changelog += "\n"
        
        return changelog

def save_changelog(self, content: str, filename="generated_docs/CHANGELOG.md"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)  # Ensure the directory exists
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info(f"Changelog saved to {filename}")

def main():
    repo_path = "."  # Current directory (change to your repo path if needed)
    
    generator = ChangelogGenerator(repo_path)
    
    # Generate Full Changelog
    full_changelog = generator.generate_full_changelog()
    save_changelog(full_changelog, "generated_docs/FULL_CHANGELOG.md")
    
    
    # Generate Release Changelog
    release_changelog = generator.generate_release_changelog()
    save_changelog(release_changelog, "generated_docs/RELEASE_CHANGELOG.md")

if __name__ == "__main__":
    main()