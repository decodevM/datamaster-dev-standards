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

    # Add type-specific colors
    type_colors = {
        "feat": "#2563eb",     # Blue
        "fix": "#dc2626",      # Red
        "docs": "#7c3aed",     # Purple
        "style": "#db2777",    # Pink
        "refactor": "#2dd4bf", # Teal
        "perf": "#f59e0b",     # Amber
        "test": "#10b981",     # Emerald
        "chore": "#6b7280"     # Gray
    }
    
    def _style_scope_tag(self, scope: str) -> str:
        return f"""<span class="scope-tag">{scope}</span>"""

    def generate(self, commits: Dict) -> str:
        today = datetime.now().strftime("%d %B %Y")
        repo_info = f"{os.getenv('REPO_OWNER')}/{os.getenv('REPO_NAME')}"

        doc = [
            "<style>",
            """
            :root {
                --primary: #2563eb;
                --surface: #ffffff;
                --surface-hover: #f8fafc;
                --text: #24292e;
                --text-light: #586069;
                --border: #e1e4e8;
                --radius: 8px;
                --shadow: 0 1px 3px rgba(0,0,0,0.12);
                --shadow-hover: 0 4px 6px rgba(0,0,0,0.1);
                --transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
                --spacing: 1rem;
            }

            .container {
                max-width: 960px;
                margin: 0 auto;
                padding: calc(var(--spacing) * 2);
                font-family: -apple-system, system-ui, sans-serif;
                line-height: 1.5;
                color: var(--text);
            }

            .header {
                background: linear-gradient(135deg, #1a365d, var(--primary));
                color: white;
                padding: calc(var(--spacing) * 3) var(--spacing);
                border-radius: calc(var(--radius) * 2);
                margin-bottom: calc(var(--spacing) * 3);
                text-align: center;
                box-shadow: var(--shadow);
            }

            .header h1 {
                font-size: 2.5rem;
                font-weight: 700;
                background: linear-gradient(to right, #fff, #e2e8f0);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .type-header {
                display: flex;
                align-items: center;
                gap: calc(var(--spacing) * 0.5);
                padding: calc(var(--spacing) * 0.75) calc(var(--spacing) * 1.5);
                border-radius: var(--radius);
                margin: calc(var(--spacing) * 2) 0;
                color: white;
                font-weight: 600;
                transition: transform var(--transition);
            }

            .type-header:hover { transform: translateX(4px); }

            .scope-tag {
                display: inline-block;
                padding: calc(var(--spacing) * 0.25) calc(var(--spacing) * 0.75);
                background: var(--surface-hover);
                border-radius: var(--radius);
                font-size: 0.875rem;
                font-weight: 500;
                box-shadow: var(--shadow);
            }

            .commit-list {
                list-style: none;
                margin: var(--spacing) 0;
            }

            .commit-item {
                background: var(--surface);
                border-radius: var(--radius);
                padding: var(--spacing);
                margin-bottom: var(--spacing);
                box-shadow: var(--shadow);
                transition: all var(--transition);
            }

            .commit-item:hover {
                transform: translateY(-2px);
                box-shadow: var(--shadow-hover);
            }

            .commit-title {
                font-weight: 600;
                margin-bottom: calc(var(--spacing) * 0.5);
            }

            .commit-meta {
                font-size: 0.875rem;
                color: var(--text-light);
            }

            .commit-body {
                background: var(--surface-hover);
                border-radius: var(--radius);
                padding: var(--spacing);
                margin: calc(var(--spacing) * 0.5) 0;
                font-family: monospace;
                white-space: pre-wrap;
            }

            details { margin: var(--spacing) 0; }
            summary { cursor: pointer; }
            summary::-webkit-details-marker { display: none; }

            /* Type colors */
            ${'.type-' + type}: { background: ${color}; }
            ${' '.join([f'.type-{type} {{ background: {color}; }}' for type, color in self.type_colors.items()])}
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
            doc.append(
                f'<div class="type-header type-{type_name}">'
                f'{emoji} {type_name.capitalize()}s'
                f'</div>'
            )

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
    
    type_colors = {
        "feat": "#2563eb",     # Blue
        "fix": "#dc2626",      # Red
        "docs": "#7c3aed",     # Purple
        "style": "#db2777",    # Pink
        "refactor": "#2dd4bf", # Teal
        "perf": "#f59e0b",     # Amber
        "test": "#10b981",     # Emerald
        "chore": "#6b7280"     # Gray
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
        version = datetime.now().strftime("v%Y.%m.%d")
        repo_info = f"{os.getenv('REPO_OWNER')}/{os.getenv('REPO_NAME')}"

        doc = [
            "<style>",
            """
            :root {
                --primary: #2563eb;
                --surface: #ffffff;
                --surface-hover: #f8fafc;
                --text: #24292e;
                --text-light: #586069;
                --border: #e1e4e8;
                --radius: 8px;
                --shadow: 0 1px 3px rgba(0,0,0,0.12);
                --shadow-hover: 0 4px 6px rgba(0,0,0,0.1);
                --transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
                --spacing: 1rem;
            }

            .container {
                max-width: 960px;
                margin: 0 auto;
                padding: calc(var(--spacing) * 2);
                font-family: -apple-system, system-ui, sans-serif;
            }

            .header {
                background: linear-gradient(135deg, #1a365d, var(--primary));
                color: white;
                padding: calc(var(--spacing) * 3) var(--spacing);
                border-radius: calc(var(--radius) * 2);
                margin-bottom: calc(var(--spacing) * 3);
                text-align: center;
                box-shadow: var(--shadow);
            }

            .header h1 {
                font-size: 2.5rem;
                font-weight: 700;
                background: linear-gradient(to right, #fff, #e2e8f0);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .scope-tag {
                display: inline-block;
                padding: calc(var(--spacing) * 0.25) calc(var(--spacing) * 0.75);
                background: var(--surface-hover);
                border-radius: var(--radius);
                font-size: 0.875rem;
                font-weight: 500;
                box-shadow: var(--shadow);
                transition: transform var(--transition);
            }

            .scope-tag:hover {
                transform: translateY(-1px);
                box-shadow: var(--shadow-hover);
            }

            .commit-list {
                list-style: none;
                margin: var(--spacing) 0;
            }

            .commit-item {
                background: var(--surface);
                border-radius: var(--radius);
                padding: var(--spacing);
                margin-bottom: var(--spacing);
                box-shadow: var(--shadow);
                transition: all var(--transition);
            }

            .commit-item:hover {
                transform: translateY(-2px);
                box-shadow: var(--shadow-hover);
            }

            .type-header {
                display: flex;
                align-items: center;
                gap: calc(var(--spacing) * 0.5);
                padding: calc(var(--spacing) * 0.75) calc(var(--spacing) * 1.5);
                border-radius: var(--radius);
                margin: calc(var(--spacing) * 2) 0;
                color: white;
                font-weight: 600;
                font-size: 1.25rem;
            }

            /* Type colors */
            ${' '.join([f'.type-{type} {{ background: {color}; }}' for type, color in type_colors.items()])}
            """,
            "</style>",
            "<div class='container'>",
            "<header class='header'>",
            f"<h1>🚀 Release {version}</h1>",
            f"<p>Released on {today}</p>",
            "</header>",
            "<h2>📋 What's Changed</h2>"
        ]

        for type_name in self.priority_order:
            if type_name not in commits or not commits[type_name]:
                continue

            emoji = self.emojis.get(type_name, "📌")
            doc.append(
                f'<div class="type-header type-{type_name}">'
                f'{emoji} {type_name.capitalize()}s'
                '</div>'
            )

            for scope, commits_list in commits[type_name].items():
                doc.append("<details open>")
                doc.append(f"<summary>{self._style_scope_tag(scope)}</summary>")
                doc.append("<ul class='commit-list'>")

                for commit in commits_list:
                    doc.extend([
                        "<li class='commit-item'>",
                        f"<div class='commit-title'>{commit['title']}</div>",
                        "</li>"
                    ])

                doc.extend([
                    "</ul>",
                    "</details>"
                ])

        doc.append("</div>")
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