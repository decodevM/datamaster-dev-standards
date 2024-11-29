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

# class MarkdownCommitReportGenerator(ReportStrategy):
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

#     def generate(self, commits: Dict) -> str:
#         today = datetime.now().strftime("%d %B %Y")

#         doc = [
#             "# 📄 Detailed Commit Report",
#             f"*Generated on {today}*\n",
#             "## 🔍 Commit Details by Type\n"
#         ]

#         for commit_type, scopes in commits.items():
#             if not scopes:
#                 continue

#             emoji = self.emojis.get(commit_type, "📌")
#             doc.append(f"# {emoji} {commit_type.capitalize()}s\n")

#             for scope, commits_list in scopes.items():
#                 doc.append(f"## 📦 `{scope}`\n")

#                 for commit in commits_list:
#                     doc.extend([
#                         f"### {commit['title']}",
#                         f"- 👤 **Author:** {commit['author']}",
#                         f"- 📅 **Date:** {commit['date']}"
#                     ])

#                     if commit['body']:
#                         doc.extend([
#                             "",
#                             "**Details:**",
#                             "```",
#                             commit['body'],
#                             "```"
#                         ])

#                     if commit['refs']:
#                         doc.append(f"🔗 **References:** {', '.join(commit['refs'])}")

#                     doc.append("\n---\n")

#         return "\n".join(doc)


# class ReleaseChangelogStrategy(ReportStrategy):
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
        
#     def generate(self, commits: Dict) -> str:
#         today = datetime.now().strftime("%d %B %Y")
#         version = datetime.now().strftime("v%Y.%m.%d")
        
#         doc = [
#             f"# 🚀 Release {version}",
#             f"*Released on {today}*\n",
#             "## Changes in this Release\n"
#         ]

#         priority_order = ['feat', 'fix', 'perf', 'refactor', 'docs', 'style', 'test', 'chore']
        
#         for type_name in priority_order:
#             if type_name not in commits or not commits[type_name]:
#                 continue
#             emoji = self.emojis.get(type_name, "📌")
#             doc.append(f"# {emoji} {type_name.capitalize()}s\n")

#             for scope, commits_list in commits[type_name].items():
#                 doc.append(f"## 📦 `{scope}`\n")
#                 for commit in commits_list:
#                     entry = [f"- {commit['title']}"]
#                     if commit['refs']:
#                         entry.append(f"  ({', '.join(commit['refs'])})")
#                     doc.append("".join(entry))
#             doc.append("")
        
#         return "\n".join(doc)


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
        repo_info = f"{os.getenv('REPO_OWNER')}/{os.getenv('REPO_NAME')}"

        doc = [
            "<div align='center'>",
            "",
            "# 📄 Detailed Commit Report",
            "",
            f"[![Last Updated]({today})](#{today.lower().replace(' ', '-')})",
            f"[![Repository]({repo_info})](https://github.com/{repo_info})",
            "",
            "</div>",
            "",
            "---",
            "",
            "## 📋 Table of Contents\n"
        ]

        # Generate TOC
        for commit_type in commits.keys():
            if commits[commit_type]:
                emoji = self.emojis.get(commit_type, "📌")
                doc.append(f"- [{emoji} {commit_type.capitalize()}s](#{commit_type}s)")

        doc.append("\n---\n")

        # Generate content
        for commit_type, scopes in commits.items():
            if not scopes:
                continue

            emoji = self.emojis.get(commit_type, "📌")
            doc.append(f"# {emoji} {commit_type.capitalize()}s {' ' * 3}<a name='{commit_type}s'></a>\n")

            for scope, commits_list in scopes.items():
                doc.append(f"<details open><summary><h2>📦 `{scope}`</h2></summary>\n")

                for commit in commits_list:
                    doc.extend([
                        "<table>",
                        "<tr>",
                        f"<td><h3>{commit['title']}</h3></td>",
                        "</tr>",
                        "<tr>",
                        "<td>",
                        f"👤 **Author:** {commit['author']}  ",
                        f"📅 **Date:** {commit['date']}",
                        "</td>",
                        "</tr>"
                    ])

                    if commit['body']:
                        doc.extend([
                            "<tr>",
                            "<td>",
                            "",
                            "**Details:**",
                            "<pre>",
                            commit['body'],
                            "</pre>",
                            "</td>",
                            "</tr>"
                        ])

                    if commit['refs']:
                        doc.extend([
                            "<tr>",
                            "<td>",
                            f"🔗 **References:** {', '.join(commit['refs'])}",
                            "</td>",
                            "</tr>"
                        ])

                    doc.extend([
                        "</table>",
                        "",
                        "<br>"
                    ])

                doc.append("</details>\n")

        return "\n".join(doc)

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
        repo_info = f"{os.getenv('REPO_OWNER')}/{os.getenv('REPO_NAME')}"
        
        doc = [
            "<div align='center'>",
            "",
            f"# 🚀 Release {version}",
            "",
            f"[![Release Date]({today})](#{today.lower().replace(' ', '-')})",
            f"[![Repository]({repo_info})](https://github.com/{repo_info})",
            "",
            "</div>",
            "",
            "---",
            "",
            "## 📋 What's Changed\n"
        ]

        priority_order = ['feat', 'fix', 'perf', 'refactor', 'docs', 'style', 'test', 'chore']
        
        for type_name in priority_order:
            if type_name not in commits or not commits[type_name]:
                continue

            emoji = self.emojis.get(type_name, "📌")
            doc.append(f"### {emoji} {type_name.capitalize()}s\n")

            for scope, commits_list in commits[type_name].items():
                doc.append(f"<details open><summary><b>📦 `{scope}`</b></summary>\n")
                doc.append("<div class='release-notes'>\n")

                for commit in commits_list:
                    entry = [
                        "<table>",
                        "<tr>",
                        f"<td>{commit['title']}</td>",
                        "</tr>"
                    ]
                    
                    if commit['refs']:
                        entry.extend([
                            "<tr>",
                            "<td>",
                            f"<sub>🔗 {', '.join(commit['refs'])}</sub>",
                            "</td>",
                            "</tr>"
                        ])
                    
                    entry.extend([
                        "</table>",
                        ""
                    ])
                    
                    doc.extend(entry)

                doc.extend([
                    "</div>",
                    "</details>\n"
                ])
        
        # Add footer
        doc.extend([
            "---",
            "",
            "<div align='center'>",
            "",
            "⭐ **Thank you for using our software!** ⭐",
            "",
            "</div>"
        ])
        
        return "\n".join(doc)

class ReportGeneratorFactory:
    @staticmethod
    def create_generator(report_type: str) -> ReportStrategy:
        generators = {
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