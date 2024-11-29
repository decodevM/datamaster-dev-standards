# # import os
# # import re
# # import requests
# # from datetime import datetime
# # from typing import Dict, List, Optional
# # import logging

# # # Configure logging
# # logging.basicConfig(level=logging.INFO)
# # logger = logging.getLogger(__name__)

# # class CommitParser:
# #     def __init__(self):
# #         self.TYPES = ["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore"]
# #         self.commit_pattern = self._create_commit_pattern()

# #     def _create_commit_pattern(self):
# #         type_regex = "|".join(self.TYPES)
# #         return re.compile(
# #             rf"^(?P<type>{type_regex})"
# #             r"\((?P<scope>[^)]+)\):\s*"
# #             r"(?P<title>[^\n]+)$",
# #             re.DOTALL,
# #         )

# #     def parse(self, message: str) -> Optional[Dict]:
# #         match = self.commit_pattern.match(message.strip())
# #         if match:
# #             return match.groupdict()
# #         return None


# # class ChangelogGenerator:
# #     def __init__(self):
# #         self.parser = CommitParser()
# #         self.github_token = os.getenv("GITHUB_TOKEN")
# #         self.repo_owner = os.getenv("REPO_OWNER")
# #         self.repo_name = os.getenv("REPO_NAME")

# #     def fetch_commits(self, branch="main") -> List[Dict]:
# #         url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/commits"
# #         headers = {
# #             "Authorization": f"token {self.github_token}",
# #             "Accept": "application/vnd.github.v3+json",
# #         }

# #         commits = []
# #         page = 1
# #         while True:
# #             response = requests.get(
# #                 url, headers=headers, params={"sha": branch, "page": page, "per_page": 100}
# #             )
# #             if response.status_code != 200:
# #                 logger.error(f"Failed to fetch commits: {response.json()}")
# #                 break

# #             data = response.json()
# #             if not data:
# #                 break

# #             commits.extend(data)
# #             page += 1

# #         return commits

# #     def categorize_commits(self, commits: List[Dict]) -> Dict[str, Dict[str, List[str]]]:
# #         categorized = {t: {} for t in self.parser.TYPES}
# #         seen_commits = set()  # Use a set to track unique commits

# #         for commit in commits:
# #             message = commit["commit"]["message"]
# #             parsed = self.parser.parse(message)
# #             if parsed:
# #                 # Create a unique identifier for each commit
# #                 unique_identifier = f"{parsed['type']}::{parsed['scope']}::{parsed['title']}"
                
# #                 if unique_identifier in seen_commits:
# #                     continue  # Skip duplicate commits
                
# #                 seen_commits.add(unique_identifier)  # Mark as seen
                
# #                 commit_type = parsed["type"]
# #                 scope = parsed["scope"]
# #                 title = parsed["title"]

# #                 if scope not in categorized[commit_type]:
# #                     categorized[commit_type][scope] = []
# #                 categorized[commit_type][scope].append(title)

# #         return categorized

# #     def generate_markdown(self, categorized_commits: Dict[str, Dict[str, List[str]]]) -> str:
# #         emojis = {
# #             "feat": "✨",
# #             "fix": "🐛",
# #             "docs": "📚",
# #             "style": "💎",
# #             "refactor": "♻️",
# #             "perf": "⚡️",
# #             "test": "🧪",
# #             "chore": "🔧",
# #         }

# #         today = datetime.now().strftime("%d %B %Y")
# #         changelog = [f"# Changelog\n\nGenerated on {today}\n"]

# #         for commit_type, scopes in categorized_commits.items():
# #             if not scopes:
# #                 continue

# #             emoji = emojis.get(commit_type, "📌")
# #             changelog.append(f"## {emoji} {commit_type.capitalize()}s\n")

# #             for scope, titles in scopes.items():
# #                 changelog.append(f"### `{scope}`\n")
# #                 for title in titles:
# #                     changelog.append(f"- {title}")

# #         return "\n".join(changelog)

# #     def generate_full_markdown(self, commits: List[Dict]) -> str:
# #         today = datetime.now().strftime("%d %B %Y")
# #         full_changelog = [f"# Full Changelog\n\nGenerated on {today}\n"]
# #         emojis = {
# #             "feat": "✨",
# #             "fix": "🐛",
# #             "docs": "📚",
# #             "style": "💎",
# #             "refactor": "♻️",
# #             "perf": "⚡️",
# #             "test": "🧪",
# #             "chore": "🔧",
# #         }
        
# #         # Group commits by type
# #         categorized_commits = {t: {} for t in self.parser.TYPES}
# #         for commit in commits:
# #             message = commit["commit"]["message"]
# #             parsed = self.parser.parse(message)
# #             if parsed:
# #                 commit_type = parsed["type"]
# #                 scope = parsed["scope"]
# #                 title = parsed["title"]
# #                 body = commit["commit"].get("body", "")  # Get the commit body
# #                 refs = commit["commit"].get("refs", "")  # Get the refs

# #                 if scope not in categorized_commits[commit_type]:
# #                     categorized_commits[commit_type][scope] = []

# #                 # Store the commit with title, body, and refs in the categorized_commits
# #                 categorized_commits[commit_type][scope].append({
# #                     "title": title,
# #                     "body": body,
# #                     "refs": refs,
# #                 })

# #         # Format categorized commits
# #         for commit_type, scopes in categorized_commits.items():
# #             if not scopes:
# #                 continue

# #             emoji = emojis.get(commit_type, "📌")
# #             full_changelog.append(f"## {emoji} {commit_type.capitalize()}s\n")

# #             for scope, commit_list in scopes.items():
# #                 full_changelog.append(f"### `{scope}`\n")
# #                 for commit in commit_list:
# #                     full_changelog.append(f"- **{commit['title']}**")  # Display title
# #                     if commit['body']:  # Only display body if it's not empty
# #                         full_changelog.append(f"  - Description: {commit['body']}")
# #                     if commit['refs']:  # Only display refs if they exist
# #                         full_changelog.append(f"  - Refs: {commit['refs']}")

# #         return "\n".join(full_changelog)

# #     def extract_refs(self, message: str) -> List[str]:
# #         """
# #         Extract references like issue numbers or PR links from the commit message.
# #         Example:
# #         - 'Fixes #123'
# #         - 'Refs #456'
# #         """
# #         refs = re.findall(r"(#\d+)", message)  # Find all occurrences of # followed by numbers
# #         return refs

# #     def save_changelog(self, content: str, filename="generated_docs/CHANGELOG.md"):
# #         os.makedirs(os.path.dirname(filename), exist_ok=True)  # Ensure the directory exists
# #         with open(filename, "w", encoding="utf-8") as f:
# #             f.write(content)
# #         logger.info(f"Changelog saved to {filename}")


# # def main():
# #     # Ensure required environment variables are set
# #     for env_var in ["GITHUB_TOKEN", "REPO_OWNER", "REPO_NAME"]:
# #         if not os.getenv(env_var):
# #             logger.error(f"Environment variable {env_var} is missing!")
# #             return

# #     branch = os.getenv("BRANCH", "main")

# #     generator = ChangelogGenerator()
# #     commits = generator.fetch_commits(branch=branch)

# #     if not commits:
# #         logger.error("No commits found. Exiting.")
# #         return

# #     categorized_commits = generator.categorize_commits(commits)
# #     release_changelog = generator.generate_markdown(categorized_commits)
# #     generator.save_changelog(release_changelog, "generated_docs/RELEASE_CHANGELOG.md")

# #     full_changelog = generator.generate_full_markdown(commits)
# #     generator.save_changelog(full_changelog, "generated_docs/FULL_CHANGELOG.md")


# # if __name__ == "__main__":
# #     main()


# #----------------------------------------------------------------------
# #----------------------------------------------------------------------
# #----------------------------------------------------------------------
# #----------------------------------------------------------------------
# #----------------------------------------------------------------------
# #----------------------------------------------------------------------
# #----------------------------------------------------------------------
# #----------------------------------------------------------------------
# #----------------------------------------------------------------------
# #----------------------------------------------------------------------
# #----------------------------------------------------------------------
# #----------------------------------------------------------------------
# #----------------------------------------------------------------------
# #----------------------------------------------------------------------
# #----------------------------------------------------------------------
# #----------------------------------------------------------------------
# #----------------------------------------------------------------------
# #----------------------------------------------------------------------
# #----------------------------------------------------------------------
# #----------------------------------------------------------------------
# #----------------------------------------------------------------------
# #----------------------------------------------------------------------




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
#             r"(?P<title>[^\n]+)\n"  # Title line
#             r"(?P<body>(?:.|\n)*?)"  # Body (can be empty)
#             r"(?:\n(?P<footer>.+))?$",  # Footer (can be empty)
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

#             if parsed:  # Only proceed if parsing was successful
#                 # Extract the footer, body, and title if available
#                 footer = parsed.get("footer", "").strip() if parsed.get("footer") else ""
#                 body = parsed.get("body", "").strip() if parsed.get("body") else ""  # Extract body

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

#                 categorized[commit_type][scope].append({
#                     "title": title,
#                     "body": body,  # Add body to the categorized commit
#                     "footer": footer  # Add footer to the categorized commit
#                 })

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

#             for scope, commit_list in scopes.items():
#                 changelog.append(f"### `{scope}`\n")
#                 for commit in commit_list:
#                     changelog.append(f"- **{commit['title']}**")  # Display title
#                     if commit['body']:  # Only display body if it's not empty
#                         changelog.append(f"  - Description: {commit['body']}")
#                     if commit['footer']:  # Only display footer if it exists
#                         changelog.append(f"  - Footer: {commit['footer']}")

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
#                 body = parsed.get("body", "")  # Get the commit body
#                 footer = parsed.get("footer", "")  # Get the commit footer

#                 if scope not in categorized_commits[commit_type]:
#                     categorized_commits[commit_type][scope] = []

#                 # Store the commit with title, body, and footer in the categorized_commits
#                 categorized_commits[commit_type][scope].append({
#                     "title": title,
#                     "body": body,
#                     "footer": footer,
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
#                     if commit['footer']:  # Only display footer if it exists
#                         full_changelog.append(f"  - Footer: {commit['footer']}")

#         return "\n".join(full_changelog)

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
# import os
# import re
# from datetime import datetime
# import requests
# from typing import Dict, Optional, List
# import logging

# # Configure logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# class CommitParser:
#     def __init__(self):
#         self.TYPES = ["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore"]
#         self.commit_pattern = self._create_commit_pattern()

#     def _create_commit_pattern(self):
#         type_regex = "|".join(self.TYPES)
#         return re.compile(
#             r"^(?P<type>" + type_regex + ")"
#             r"\((?P<scope>[^)]+)\):\s*"
#             r"(?P<title>[^\n]+)"
#             r"(?:(?P<body>[\s\S]*?))?"  # Non-greedy match for the body
#             r"(?:\nRefs:\s*(?P<refs>#[A-Za-z0-9-]+(?:,\s*#[A-Za-z0-9-]+)*))?"  # Non-greedy match for the footer
#             r"$", re.DOTALL
#         )

#     def parse(self, message: str) -> Optional[Dict]:
#         try:
#             if not message or not isinstance(message, str):
#                 logger.warning(f"Invalid message format: {message}")
#                 return None

#             message = message.strip()
#             match = self.commit_pattern.match(message)
            
#             if not match:
#                 logger.debug(f"No match found for message: {message}")
#                 return None

#             result = match.groupdict()
            
#             # Safe string operations with null checks
#             return {
#                 "type": result.get("type", ""),
#                 "scope": result.get("scope", ""),
#                 "title": result.get("title", ""),
#                 "body": result.get("body", "").strip() if result.get("body") else "",  # Ensure body is stripped
#                 "refs": [ref.strip() for ref in result.get("refs", "").split(",")] if result.get("refs") else []
#             }
            
#         except Exception as e:
#             logger.error(f"Error parsing commit message: {e}")
#             return None

# class CommitDocument:
#     def __init__(self):
#         self.parser = CommitParser()
#         self.github_token = os.getenv('GITHUB_TOKEN')
#         self.repo_owner = os.getenv('REPO_OWNER')
#         self.repo_name = os.getenv('REPO_NAME')

#     def fetch_commits(self, branch="main"):
#         url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/commits"
#         headers = {
#             "Authorization": f"token {self.github_token}",
#             "Accept": "application/vnd.github.v3+json"
#         }
        
#         commits = []
#         page = 1
        
#         while True:
#             try:
#                 response = requests.get(
#                     url, 
#                     headers=headers,
#                     params={"sha": branch, "page": page}
#                 )
#                 response.raise_for_status()
                
#                 data = response.json()
#                 if not data:
#                     break
                    
#                 commits.extend(data)
#                 page += 1
                
#             except Exception as e:
#                 logger.error(f"Error fetching commits: {e}")
#         return commits

#     def categorize_commits(self, commits):
#         categorized = {t: [] for t in self.parser.TYPES}
        
#         for commit in commits:
#             message = commit["commit"]["message"]
#             author = commit["commit"]["author"]["name"]
#             date = datetime.strptime(
#                 commit["commit"]["author"]["date"], 
#                 "%Y-%m-%dT%H:%M:%SZ"
#             ).strftime("%d %B %Y %H:%M")
            
#             parsed = self.parser.parse(message)
#             if parsed:
#                 commit_info = {
#                     **parsed,
#                     "date": date,
#                     "author": author
#                 }
#                 categorized[parsed["type"]].append(commit_info)
                
#         return categorized

#     def generate_markdown(self, categorized_commits):
#         emojis = {
#             "feat": "✨",
#             "fix": "🐛",
#             "docs": "📚",
#             "style": "💎",
#             "refactor": "♻️",
#             "perf": "⚡️",
#             "test": "🧪",
#             "chore": "🔧"
#         }
        
#         today = datetime.now().strftime("%d %B %Y")
        
#         doc = [
#             "# 📄 Commit Report",
#             f"*Generated on {today}*\n",
#             "## 🏢 Project Commits\n"
#         ]
        
#         for commit_type in self.parser.TYPES:
#             commits = categorized_commits[commit_type]
#             if not commits:
#                 continue
                
#             emoji = emojis.get(commit_type, "📌")
#             doc.append(f"### {emoji} {commit_type.capitalize()}s\n")
            
#             for commit in commits:
#                 doc.extend([
#                     f"#### `{commit['scope']}` {commit['title']}",
#                     f"*{commit['author']} - {commit['date']}*\n",
#                     f"{commit['body']}\n" if commit['body'] else "",
#                     f"🔗 {', '.join(commit['refs'])}\n" if commit['refs'] else "",
#                     "---\n"


                    
#                 ])
                
#         return "\n".join(filter(None, doc))

#     def save_document(self, content, filename="generated_docs/commit_document.md"):
#         os.makedirs(os.path.dirname(filename), exist_ok=True)
#         with open(filename, 'w', encoding='utf-8') as f:
#             f.write(content)
#         print(f"✅ Document saved to: {filename}")

# def main():
#     doc_generator = CommitDocument()
#     commits = doc_generator.fetch_commits()
    
#     if not commits:
#         print("❌ No commits found")
#         return
        
#     categorized = doc_generator.categorize_commits(commits)
#     markdown = doc_generator.generate_markdown(categorized)
#     doc_generator.save_document(markdown)

# if __name__ == "__main__":
#     main()




# import os
# import re
# from datetime import datetime
# import requests
# from typing import Dict, Optional, List
# import logging

# # Configure logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)


# class CommitParser:
#     def __init__(self):
#         self.TYPES = ["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore"]
#         self.commit_pattern = self._create_commit_pattern()

#     def _create_commit_pattern(self):
#         type_regex = "|".join(self.TYPES)
#         return re.compile(
#             r"^(?P<type>" + type_regex + r")"
#             r"\((?P<scope>[^)]+)\):\s*"
#             r"(?P<title>[^\n]+)"
#             r"(?:(?P<body>[\s\S]*?))?"  # Non-greedy match for the body
#             r"(?:\nRefs:\s*(?P<refs>#[A-Za-z0-9-]+(?:,\s*#[A-Za-z0-9-]+)*))?"  # Non-greedy match for the footer
#             r"$", re.DOTALL
#         )

#     def parse(self, message: str) -> Optional[Dict]:
#         try:
#             if not message or not isinstance(message, str):
#                 logger.warning(f"Invalid message format: {message}")
#                 return None

#             message = message.strip()
#             match = self.commit_pattern.match(message)

#             if not match:
#                 logger.debug(f"No match found for message: {message}")
#                 return None

#             result = match.groupdict()

#             return {
#                 "type": result.get("type", ""),
#                 "scope": result.get("scope", ""),
#                 "title": result.get("title", ""),
#                 "body": result.get("body", "").strip() if result.get("body") else None,
#                 "refs": [ref.strip() for ref in result.get("refs", "").split(",")] if result.get("refs") else []
#             }

#         except Exception as e:
#             logger.error(f"Error parsing commit message: {e}")
#             return None


# class CommitDocument:
#     def __init__(self):
#         self.parser = CommitParser()
#         self.github_token = os.getenv('GITHUB_TOKEN')
#         self.repo_owner = os.getenv('REPO_OWNER')
#         self.repo_name = os.getenv('REPO_NAME')

#     def fetch_commits(self, branch="main"):
#         url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/commits"
#         headers = {
#             "Authorization": f"token {self.github_token}",
#             "Accept": "application/vnd.github.v3+json"
#         }

#         commits = []
#         page = 1

#         while True:
#             try:
#                 response = requests.get(
#                     url,
#                     headers=headers,
#                     params={"sha": branch, "page": page}
#                 )
#                 response.raise_for_status()

#                 data = response.json()
#                 if not data:
#                     break

#                 commits.extend(data)
#                 page += 1

#             except Exception as e:
#                 logger.error(f"Error fetching commits: {e}")
#                 break

#         return commits

#     def categorize_commits(self, commits):
#         categorized = {t: {} for t in self.parser.TYPES}  # Group by type and scope
#         seen = set()  # Set to track unique commit identifiers

#         for commit in commits:
#             message = commit["commit"]["message"]
#             author = commit["commit"]["author"]["name"]
#             date = datetime.strptime(
#                 commit["commit"]["author"]["date"],
#                 "%Y-%m-%dT%H:%M:%SZ"
#             ).strftime("%d %B %Y %H:%M")

#             parsed = self.parser.parse(message)
#             if parsed:
#                 # Create a unique identifier for the commit
#                 commit_id = (
#                     parsed["type"],
#                     parsed["scope"],
#                     parsed["title"],
#                     parsed["body"],
#                     tuple(parsed["refs"])
#                 )

#                 if commit_id in seen:  # Skip duplicates
#                     continue

#                 seen.add(commit_id)  # Mark this commit as seen

#                 commit_info = {
#                     **parsed,
#                     "date": date,
#                     "author": author
#                 }

#                 # Add to categorized commits by type and scope
#                 scope_group = categorized[parsed["type"]].setdefault(parsed["scope"], [])
#                 scope_group.append(commit_info)

#         return categorized

#     def generate_markdown(self, categorized_commits):
#         emojis = {
#             "feat": "✨",
#             "fix": "🐛",
#             "docs": "📚",
#             "style": "💎",
#             "refactor": "♻️",
#             "perf": "⚡️",
#             "test": "🧪",
#             "chore": "🔧"
#         }

#         today = datetime.now().strftime("%d %B %Y")

#         doc = [
#             "# 📄 Commit Report",
#             f"*Generated on {today}*\n",
#             "## 🏢 Project Commits\n"
#         ]

#         for commit_type, scopes in categorized_commits.items():
#             if not scopes:
#                 continue

#             emoji = emojis.get(commit_type, "📌")
#             doc.append(f"### {emoji} {commit_type.capitalize()}s\n")

#             for scope, commits in scopes.items():
#                 doc.append(f"#### `{scope}`\n")

#                 for commit in commits:
#                     # Title with author and date
#                     doc.append(f"- **{commit['title']}**")
#                     doc.append(f"  *{commit['author']} - {commit['date']}*")

#                     # Add body with indentation based on leading spaces
#                     if commit['body'] or commit['refs']:
#                         # print('body: ' + commit['body'])
#                         doc.append(f"\n\t**Description**\n")  # Add a description heading
#                         doc.append(f"\t```text")
#                         if commit['body']:  # Open the code block
#                             for line in commit['body'].splitlines():
#                                 doc.append(f"\t{line}")          # Add each line of the body with tab-based indentation

#                             doc.append(f"\n")  

#                         # Add refs with indentation
#                         if commit['refs']:    # Add a refs heading
#                             for ref in commit['refs']:
#                                 doc.append(f"\t🔗 {ref.strip()}")  # Tab for each ref
#                                 doc.append(f"\t🔗 {ref.strip()}")  # Tab for each ref
#                         doc.append(f"\t```")                  # Close the code block


                    

#                 doc.append("---")  # Separator for each scope

#         return "\n".join(doc)
    

#     def save_document(self, content, filename="generated_docs/commit_document.md"):
#         os.makedirs(os.path.dirname(filename), exist_ok=True)
#         with open(filename, 'w', encoding='utf-8') as f:
#             f.write(content)
#         print(f"✅ Document saved to: {filename}")


# def main():
#     doc_generator = CommitDocument()
#     commits = doc_generator.fetch_commits()

#     if not commits:
#         print("❌ No commits found")
#         return

#     categorized = doc_generator.categorize_commits(commits)
#     markdown = doc_generator.generate_markdown(categorized)
#     doc_generator.save_document(markdown)


# if __name__ == "__main__":
#     main()







#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------



# import os
# import re
# from datetime import datetime
# import requests
# from typing import Dict, Optional, List
# import logging
# from abc import ABC, abstractmethod

# # Configure logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# # Interface for Commit Fetching
# class CommitFetcher(ABC):
#     @abstractmethod
#     def fetch_commits(self, branch="main") -> List[Dict]:
#         pass

# # GitHub implementation of CommitFetcher
# class GitHubCommitFetcher(CommitFetcher):
#     def __init__(self, github_token, repo_owner, repo_name):
#         self.github_token = github_token
#         self.repo_owner = repo_owner
#         self.repo_name = repo_name

#     def fetch_commits(self, branch="main") -> List[Dict]:
#         url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/commits"
#         headers = {
#             "Authorization": f"token {self.github_token}",
#             "Accept": "application/vnd.github.v3+json"
#         }

#         commits = []
#         page = 1

#         while True:
#             try:
#                 response = requests.get(
#                     url,
#                     headers=headers,
#                     params={"sha": branch, "page": page}
#                 )
#                 response.raise_for_status()

#                 data = response.json()
#                 if not data:
#                     break

#                 commits.extend(data)
#                 page += 1

#             except Exception as e:
#                 logger.error(f"Error fetching commits: {e}")
#                 break

#         return commits

# # Interface for Commit Parsing
# class CommitParser(ABC):
#     @abstractmethod
#     def parse(self, message: str) -> Optional[Dict]:
#         pass

# # Concrete CommitParser implementation
# class BasicCommitParser(CommitParser):
#     TYPES = ["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore"]

#     def __init__(self):
#         self.commit_pattern = self._create_commit_pattern()

#     def _create_commit_pattern(self):
#         type_regex = "|".join(self.TYPES)
#         return re.compile(
#             r"^(?P<type>" + type_regex + r")"
#             r"\((?P<scope>[^)]+)\):\s*"
#             r"(?P<title>[^\n]+)"
#             r"(?:(?P<body>[\s\S]*?))?"
#             r"(?:\nRefs:\s*(?P<refs>#[A-Za-z0-9-]+(?:,\s*#[A-Za-z0-9-]+)*))?"
#             r"$", re.DOTALL
#         )

#     def parse(self, message: str) -> Optional[Dict]:
#         if not message or not isinstance(message, str):
#             logger.warning(f"Invalid message format: {message}")
#             return None

#         message = message.strip()
#         match = self.commit_pattern.match(message)

#         if not match:
#             logger.debug(f"No match found for message: {message}")
#             return None

#         result = match.groupdict()

#         return {
#             "type": result.get("type", ""),
#             "scope": result.get("scope", ""),
#             "title": result.get("title", ""),
#             "body": result.get("body", "").strip() if result.get("body") else None,
#             "refs": [ref.strip() for ref in result.get("refs", "").split(",")] if result.get("refs") else []
#         }

# # Interface for Report Generation
# class CommitReportGenerator(ABC):
#     @abstractmethod
#     def generate_report(self, categorized_commits) -> str:
#         pass

# # Concrete CommitReportGenerator for Markdown
# class MarkdownCommitReportGenerator(CommitReportGenerator):
#     emojis = {
#         "feat": "✨",
#         "fix": "🐛",
#         "docs": "📚",
#         "style": "💎",
#         "refactor": "♻️",
#         "perf": "⚡️",
#         "test": "🧪",
#         "chore": "🔧"
#     }

#     def generate_report(self, categorized_commits) -> str:
#         today = datetime.now().strftime("%d %B %Y")

#         doc = [
#             "# 📄 Commit Report",
#             f"*Generated on {today}*\n",
#             "## 🏢 Project Commits\n"
#         ]

#         for commit_type, scopes in categorized_commits.items():
#             if not scopes:
#                 continue

#             emoji = self.emojis.get(commit_type, "📌")
#             doc.append(f"### {emoji} {commit_type.capitalize()}s\n")

#             for scope, commits in scopes.items():
#                 doc.append(f"#### `{scope}`\n")

#                 for commit in commits:
#                     # Title with author and date
#                     doc.append(f"- **{commit['title']}**")
#                     doc.append(f"  *{commit['author']} - {commit['date']}*")

#                     # Add body with indentation based on leading spaces
#                     if commit['body'] or commit['refs']:
#                         doc.append(f"\n\t**Description**\n")
#                         doc.append(f"\t```text")
#                         if commit['body']:
#                             for line in commit['body'].splitlines():
#                                 doc.append(f"\t{line}")

#                             doc.append(f"\n")

#                         if commit['refs']:
#                             for ref in commit['refs']:
#                                 doc.append(f"\t🔗 {ref.strip()}")
#                         doc.append(f"\t```")

#                 doc.append("---")

#         return "\n".join(doc)

# # Factory class to create Commit Report Generators
# class CommitReportGeneratorFactory:
#     @staticmethod
#     def create_report_generator(format_type: str) -> CommitReportGenerator:
#         if format_type == "markdown":
#             return MarkdownCommitReportGenerator()
#         # Add other formats as needed (e.g., HTML)
#         raise ValueError(f"Unknown report format: {format_type}")

# # Commit Document Manager
# class CommitDocumentManager:
#     def __init__(self, commit_fetcher: CommitFetcher, commit_parser: CommitParser, report_generator: CommitReportGenerator):
#         self.commit_fetcher = commit_fetcher
#         self.commit_parser = commit_parser
#         self.report_generator = report_generator

#     def generate_document(self):
#         commits = self.commit_fetcher.fetch_commits()
#         categorized = self.categorize_commits(commits)
#         markdown_report = self.report_generator.generate_report(categorized)
#         self.save_document(markdown_report)

#     def categorize_commits(self, commits) -> Dict:
#         categorized = {t: {} for t in self.commit_parser.TYPES}
#         seen = set()

#         for commit in commits:
#             message = commit["commit"]["message"]
#             author = commit["commit"]["author"]["name"]
#             date = datetime.strptime(commit["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ").strftime("%d %B %Y %H:%M")

#             parsed = self.commit_parser.parse(message)
#             if parsed:
#                 commit_id = (
#                     parsed["type"],
#                     parsed["scope"],
#                     parsed["title"],
#                     parsed["body"],
#                     tuple(parsed["refs"])
#                 )

#                 if commit_id not in seen:
#                     seen.add(commit_id)

#                     if parsed["scope"] not in categorized[parsed["type"]]:
#                         categorized[parsed["type"]][parsed["scope"]] = []

#                     categorized[parsed["type"]][parsed["scope"]].append({
#                         "title": parsed["title"],
#                         "body": parsed["body"] or "",
#                         "author": author,
#                         "date": date,
#                         "refs": parsed["refs"]
#                     })

#         return categorized
    
#     def save_document(self, content, filename="generated_docs/commit_document.md"):
        
#         filename = filename + f"_{datetime.now().strftime('%Y-%m-%d')}"
#         os.makedirs(os.path.dirname(filename), exist_ok=True)
#         with open(filename, 'w', encoding='utf-8') as file:
#             file.write(content)
#         print(f"✅ Document saved to: {filename}")




# # Client code
# def main():
#     # Setup GitHub credentials and repository details

#     github_token = os.getenv('GITHUB_TOKEN')
#     repo_owner = os.getenv('REPO_OWNER')
#     repo_name = os.getenv('REPO_NAME')

#     # Create instances of the fetcher, parser, and report generator
#     commit_fetcher = GitHubCommitFetcher(github_token, repo_owner, repo_name)
#     commit_parser = BasicCommitParser()
#     report_generator = CommitReportGeneratorFactory.create_report_generator("markdown")

#     # Create Commit Document Manager
#     document_manager = CommitDocumentManager(commit_fetcher, commit_parser, report_generator)

#     # Generate and save the report
#     document_manager.generate_document()

# if __name__ == "__main__":
#     main()












import os
import re
from datetime import datetime
import requests
from typing import Dict, Optional, List
from abc import ABC, abstractmethod
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base classes and interfaces
class CommitFetcher(ABC):
    @abstractmethod
    def fetch_commits(self, branch="main") -> List[Dict]:
        pass

class CommitParser(ABC):
    @abstractmethod
    def parse(self, message: str) -> Optional[Dict]:
        pass

class ReportStrategy(ABC):
    @abstractmethod
    def generate(self, commits: Dict) -> str:
        pass

# Concrete implementations
class GitHubCommitFetcher(CommitFetcher):
    def __init__(self, github_token: str, repo_owner: str, repo_name: str):
        self.github_token = github_token
        self.repo_owner = repo_owner
        self.repo_name = repo_name

    def fetch_commits(self, branch="main") -> List[Dict]:
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
                break

        return commits

class BasicCommitParser(CommitParser):
    TYPES = ["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore"]

    def __init__(self):
        self.commit_pattern = self._create_commit_pattern()

    def _create_commit_pattern(self):
        type_regex = "|".join(self.TYPES)
        return re.compile(
            r"^(?P<type>" + type_regex + r")"
            r"\((?P<scope>[^)]+)\):\s*"
            r"(?P<title>[^\n]+)"
            r"(?:(?P<body>[\s\S]*?))?"
            r"(?:\nRefs:\s*(?P<refs>#[A-Za-z0-9-]+(?:,\s*#[A-Za-z0-9-]+)*))?"
            r"$", re.DOTALL
        )

    def parse(self, message: str) -> Optional[Dict]:
        if not message or not isinstance(message, str):
            logger.warning(f"Invalid message format: {message}")
            return None

        message = message.strip()
        match = self.commit_pattern.match(message)

        if not match:
            logger.debug(f"No match found for message: {message}")
            return None

        result = match.groupdict()

        return {
            "type": result.get("type", ""),
            "scope": result.get("scope", ""),
            "title": result.get("title", ""),
            "body": result.get("body", "").strip() if result.get("body") else None,
            "refs": [ref.strip() for ref in result.get("refs", "").split(",")] if result.get("refs") else []
        }

class MarkdownCommitReportGenerator(ReportStrategy):
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

    def generate(self, commits: Dict) -> str:
        today = datetime.now().strftime("%d %B %Y")

        doc = [
            "# 📄 Detailed Commit Report",
            f"*Generated on {today}*\n",
            "## 🔍 Commit Details by Type\n"
        ]

        for commit_type, scopes in commits.items():
            if not scopes:
                continue

            emoji = self.emojis.get(commit_type, "📌")
            doc.append(f"# {emoji} {commit_type.capitalize()}s\n")

            for scope, commits_list in scopes.items():
                doc.append(f"## 📦 `{scope}`\n")

                for commit in commits_list:
                    doc.extend([
                        f"### {commit['title']}",
                        f"- 👤 **Author:** {commit['author']}",
                        f"- 📅 **Date:** {commit['date']}"
                    ])

                    if commit['body']:
                        doc.extend([
                            "",
                            "**Details:**",
                            "```",
                            commit['body'],
                            "```"
                        ])

                    if commit['refs']:
                        doc.append(f"🔗 **References:** {', '.join(commit['refs'])}")

                    doc.append("\n---\n")

        return "\n".join(doc)

# class FullChangelogStrategy(ReportStrategy):
#     def generate(self, commits: Dict) -> str:
#         today = datetime.now().strftime("%d %B %Y")
#         doc = [
#             "# 📑 Full Changelog",
#             f"*Generated on {today}*\n",
#             "## Complete Changes History\n"
#         ]

#         for type_name, scopes in commits.items():
#             if not scopes:
#                 continue

#             doc.append(f"# {type_name.upper()}\n")
#             for scope, commits_list in scopes.items():
#                 doc.append(f"## {scope}")
#                 for commit in commits_list:
#                     doc.extend([
#                         f"### {commit['title']}",
#                         f"- 👤 **Author:** {commit['author']}",
#                         f"- 📅 **Date:** {commit['date']}"
#                     ])
#                     if commit['body']:
#                         doc.append(f"  - Details: {commit['body']}")
#                     if commit['refs']:
#                         doc.append(f"  - References: {', '.join(commit['refs'])}")
#                 doc.append("")
        
#         return "\n".join(doc)

class ReleaseChangelogStrategy(ReportStrategy):
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
        
    def generate(self, commits: Dict) -> str:
        today = datetime.now().strftime("%d %B %Y")
        version = datetime.now().strftime("v%Y.%m.%d")
        
        doc = [
            f"# 🚀 Release {version}",
            f"*Released on {today}*\n",
            "## Changes in this Release\n"
        ]

        priority_order = ['feat', 'fix', 'perf', 'refactor', 'docs', 'style', 'test', 'chore']
        
        for type_name in priority_order:
            if type_name not in commits or not commits[type_name]:
                continue
            emoji = self.emojis.get(type_name, "📌")
            doc.append(f"# {emoji} {type_name.capitalize()}s\n")

            for scope, commits_list in commits[type_name].items():
                doc.append(f"## 📦 `{scope}`\n")
                for commit in commits_list:
                    entry = [f"- {commit['title']}"]
                    if commit['refs']:
                        entry.append(f"  ({', '.join(commit['refs'])})")
                    doc.append("".join(entry))
            doc.append("")
        
        return "\n".join(doc)

class ReportGeneratorFactory:
    @staticmethod
    def create_generator(report_type: str) -> ReportStrategy:
        generators = {
            # 'full': FullChangelogStrategy(),
            'release': ReleaseChangelogStrategy(),
            'markdown': MarkdownCommitReportGenerator()
        }
        return generators.get(report_type)

class CommitDocumentManager:
    def __init__(self, commit_fetcher: CommitFetcher, commit_parser: CommitParser):
        self.commit_fetcher = commit_fetcher
        self.commit_parser = commit_parser

    def categorize_commits(self, commits) -> Dict:
        categorized = {t: {} for t in BasicCommitParser.TYPES}
        seen = set()

        for commit in commits:
            message = commit["commit"]["message"]
            author = commit["commit"]["author"]["name"]
            date = datetime.strptime(
                commit["commit"]["author"]["date"], 
                "%Y-%m-%dT%H:%M:%SZ"
            ).strftime("%d %B %Y %H:%M")

            parsed = self.commit_parser.parse(message)
            if parsed:
                commit_id = (
                    parsed["type"],
                    parsed["scope"],
                    parsed["title"],
                    parsed["body"],
                    tuple(parsed["refs"])
                )

                if commit_id not in seen:
                    seen.add(commit_id)
                    if parsed["scope"] not in categorized[parsed["type"]]:
                        categorized[parsed["type"]][parsed["scope"]] = []

                    categorized[parsed["type"]][parsed["scope"]].append({
                        "title": parsed["title"],
                        "body": parsed["body"] or "",
                        "author": author,
                        "date": date,
                        "refs": parsed["refs"]
                    })

        return categorized

class EnhancedCommitDocumentManager(CommitDocumentManager):
    def __init__(self, commit_fetcher: CommitFetcher, commit_parser: CommitParser):
        super().__init__(commit_fetcher, commit_parser)
        self.reports = {}

    def generate_all_documents(self):
        commits = self.commit_fetcher.fetch_commits()
        categorized = self.categorize_commits(commits)
        
        generators = {
            # 'full_changelog': ReportGeneratorFactory.create_generator('full'),
            'release_notes': ReportGeneratorFactory.create_generator('release'),
            'commit_report': ReportGeneratorFactory.create_generator('markdown')
        }

        for report_name, generator in generators.items():
            content = generator.generate(categorized)
            self.save_document(content, f"generated_docs/{report_name}.md")

    def save_document(self, content: str, base_filename: str):
        filename = f"{os.path.splitext(base_filename)[0]}_{datetime.now().strftime('%Y-%m-%d')}.md"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
        logger.info(f"✅ Generated {filename}")

def main():
    # Setup GitHub credentials
    github_token = os.getenv('GITHUB_TOKEN')
    repo_owner = os.getenv('REPO_OWNER')
    repo_name = os.getenv('REPO_NAME')

    if not all([github_token, repo_owner, repo_name]):
        logger.error("Missing required environment variables")
        return

    try:
        # Create components
        commit_fetcher = GitHubCommitFetcher(github_token, repo_owner, repo_name)
        commit_parser = BasicCommitParser()

        # Create document manager and generate reports
        document_manager = EnhancedCommitDocumentManager(commit_fetcher, commit_parser)
        document_manager.generate_all_documents()
        
        logger.info("✅ Successfully generated all reports")
    except Exception as e:
        logger.error(f"Error generating reports: {e}")

if __name__ == "__main__":
    main()