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
    
    priority_order = [
        'feat',    # New features first
        'fix',     # Bug fixes second
        'perf',    # Performance improvements
        'refactor',# Code refactoring
        'docs',    # Documentation changes
        'style',   # Style changes
        'test',    # Test changes
        'chore'    # Maintenance tasks last
    ]
    
    def _style_scope_tag(self, scope: str) -> str:
        return f"""<span class="scope-tag">{scope}</span>"""

    def generate(self, commits: Dict) -> str:
        today = datetime.now().strftime("%d %B %Y")
        repo_info = f"{os.getenv('REPO_OWNER')}/{os.getenv('REPO_NAME')}"

        doc = [
            "<style>",
            """
            :root {
                --color-bg: #ffffff;
                --color-text: #24292e;
                --color-text-secondary: #586069;
                --color-border: #e1e4e8;
                --color-surface: #f6f8fa;
                --radius-base: 8px;
                --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
                --shadow-md: 0 4px 6px rgba(0,0,0,0.05);
            }

            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                line-height: 1.5;
                color: var(--color-text);
            }

            .container {
                max-width: 960px;
                margin: 0 auto;
                padding: 2rem;
            }

            .header {
                text-align: center;
                margin-bottom: 3rem;
            }

            .scope-tag {
                display: inline-block;
                padding: 0.25rem 0.75rem;
                background: var(--color-surface);
                border-radius: var(--radius-base);
                font-size: 0.875rem;
                font-weight: 500;
                color: var(--color-text);
                margin: 0.5rem 0;
            }

            .commit-list {
                list-style: none;
                margin: 1rem 0;
            }

            .commit-item {
                background: var(--color-bg);
                border: 1px solid var(--color-border);
                border-radius: var(--radius-base);
                padding: 1rem;
                margin-bottom: 1rem;
                transition: transform 0.2s, box-shadow 0.2s;
            }

            .commit-item:hover {
                transform: translateY(-2px);
                box-shadow: var(--shadow-md);
            }

            .commit-title {
                font-size: 1rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
            }

            .commit-meta {
                font-size: 0.875rem;
                color: var(--color-text-secondary);
                margin-bottom: 0.5rem;
            }

            .commit-body {
                background: var(--color-surface);
                border-radius: var(--radius-base);
                padding: 1rem;
                margin: 0.5rem 0;
                font-family: monospace;
                white-space: pre-wrap;
                font-size: 0.875rem;
            }

            details {
                margin: 1rem 0;
            }

            summary {
                cursor: pointer;
                margin-bottom: 1rem;
            }

            summary::-webkit-details-marker {
                display: none;
            }
            """,
            "</style>",
            "<div class='container'>",
            "<header class='header'>",
            f"<h1>📄 Commit Report</h1>",
            f"<p>Generated on {today}</p>",
            "</header>"
        ]

        for type_name in self.priority_order:
            if type_name not in commits or not commits[type_name]:
                continue

            emoji = self.emojis.get(type_name, "📌")
            doc.append(f"<h2>{emoji} {type_name.capitalize()}s</h2>")

            for scope, commits_list in commits[type_name].items():
                doc.append("<details open>")
                doc.append(f"<summary>{self._style_scope_tag(scope)}</summary>")
                doc.append("<ul class='commit-list'>")

                for commit in commits_list:
                    doc.extend([
                        "<li class='commit-item'>",
                        f"<div class='commit-title'>{commit['title']}</div>",
                        f"<div class='commit-meta'>👤 {commit['author']} • 📅 {commit['date']}</div>"
                    ])

                    if commit['body']:
                        doc.extend([
                            "<div class='commit-body'>",
                            commit['body'],
                            "</div>"
                        ])

                    if commit['refs']:
                        doc.append(f"<div class='commit-meta'>🔗 {', '.join(commit['refs'])}</div>")

                    doc.append("</li>")

                doc.extend([
                    "</ul>",
                    "</details>"
                ])

        doc.append("</div>")
        return '\n'.join(doc)

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

    def _style_scope_tag(self, scope: str) -> str:
        return f"""<kbd style="
            background-color: #353543;
            color: white;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: bold;
            font-family: monospace;
        ">{scope}</kbd>"""
        
    def generate(self, commits: Dict) -> str:
        today = datetime.now().strftime("%d %B %Y")
        version = datetime.now().strftime("v%Y.%m.%d")
        repo_info = f"{os.getenv('REPO_OWNER')}/{os.getenv('REPO_NAME')}"
        
        doc = [
            "<style>",
             """
            :root {
                --md-sys-color-primary: #006495;
                --md-sys-color-surface: #fdfbff;
                --md-sys-color-surface-variant: #dde3ea;
                --md-sys-color-on-surface: #1a1c1e;
                --md-sys-color-on-surface-variant: #41474d;
                --md-elevation-1: 0px 1px 3px 1px rgba(0, 0, 0, 0.15);
                --md-elevation-2: 0px 2px 6px 2px rgba(0, 0, 0, 0.15);
            }

            .md3-surface {
                background-color: var(--md-sys-color-surface);
                border-radius: 16px;
                padding: 16px;
                margin: 8px 0;
                box-shadow: var(--md-elevation-1);
                transition: box-shadow 0.2s;
            }

            .md3-surface:hover {
                box-shadow: var(--md-elevation-2);
            }

            .md3-chip {
                display: inline-flex;
                align-items: center;
                height: 32px;
                padding: 0 12px;
                border-radius: 8px;
                background: var(--md-sys-color-surface-variant);
                color: var(--md-sys-color-on-surface-variant);
                font-size: 14px;
                font-weight: 500;
                line-height: 20px;
                user-select: none;
            }

            .md3-list {
                list-style: none;
                padding: 8px;
                margin: 0;
            }

            .md3-list-item {
                margin: 8px 0;
            }

            .md3-headline-large {
                font-size: 32px;
                line-height: 40px;
                font-weight: 400;
                margin: 24px 0 16px;
            }

            .md3-headline-medium {
                font-size: 28px;
                line-height: 36px;
                font-weight: 400;
                margin: 24px 0 16px;
            }

            .md3-body-large {
                font-size: 16px;
                line-height: 24px;
                font-weight: 400;
            }

            .md3-body-medium {
                font-size: 14px;
                line-height: 20px;
                font-weight: 400;
                color: var(--md-sys-color-on-surface-variant);
            }

            .md3-code {
                background: var(--md-sys-color-surface-variant);
                border-radius: 8px;
                padding: 16px;
                margin: 8px 0;
                font-family: monospace;
                white-space: pre-wrap;
            }

            details summary {
                cursor: pointer;
                list-style: none;
            }

            details summary::-webkit-details-marker {
                display: none;
            }
            """,
            "</style>",
            "<div align='center'>",
            f"<h1 class='md3-headline-large'>🚀 Release {version}</h1>",
            f"<p class='md3-body-medium'>Released on {today}</p>",
            "</div>",
            "<h2 class='md3-headline-medium'>📋 What's Changed</h2>"
        ]

        priority_order = ['feat', 'fix', 'perf', 'refactor', 'docs', 'style', 'test', 'chore']

        for type_name in priority_order:
            if type_name not in commits or not commits[type_name]:
                continue

            emoji = self.emojis.get(type_name, "📌")
            doc.append(f"<h3 class='md3-headline-small'>{emoji} {type_name.capitalize()}s</h3>")

            for scope, commits_list in commits[type_name].items():
                doc.append("<details open>")
                doc.append(f"<summary>{self._style_scope_tag(scope)}</summary>")
                doc.append("<ul class='md3-list'>")

                for commit in commits_list:
                    doc.extend([
                        "<li class='md3-list-item'>",
                        "<div class='md3-surface'>",
                        f"<div class='md3-body-large'>{commit['title']}</div>",
                        "</div>",
                        "</li>"
                    ])

                doc.extend([
                    "</ul>",
                    "</details>"
                ])

        return '\n'.join(doc)

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