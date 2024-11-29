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



class StyleConfig:
    # Type-specific colors and emojis
    TYPE_STYLES = {
        "feat": {"emoji": "✨", "color": "#2563eb"},    # Blue
        "fix": {"emoji": "🐛", "color": "#dc2626"},     # Red
        "docs": {"emoji": "📚", "color": "#7c3aed"},    # Purple
        "style": {"emoji": "💎", "color": "#db2777"},   # Pink
        "refactor": {"emoji": "♻️", "color": "#2dd4bf"},# Teal
        "perf": {"emoji": "⚡️", "color": "#f59e0b"},   # Amber
        "test": {"emoji": "🧪", "color": "#10b981"},    # Emerald
        "chore": {"emoji": "🔧", "color": "#6b7280"}    # Gray
    }

    # Priority order for commit types
    PRIORITY_ORDER = [
        'feat',     # New features first
        'fix',      # Bug fixes second
        'perf',     # Performance improvements
        'refactor', # Code refactoring
        'docs',     # Documentation changes
        'style',    # Style changes
        'test',     # Test changes
        'chore'     # Maintenance tasks last
    ]

    # Base styles for dark theme
    BASE_STYLES = """
        :root {
            --color-bg: #353543;
            --color-surface: #333355;
            --color-elevated: #3d3d4d;
            --color-text: #ffffff;
            --color-text-secondary: #e2e8f0;
            --color-border: rgba(255, 255, 255, 0.1);
            --radius-base: 8px;
            --radius-lg: 16px;
            --shadow-sm: 0 2px 4px rgba(0,0,0,0.2);
            --shadow-md: 0 4px 8px rgba(0,0,0,0.3);
            --transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background: var(--color-bg);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: var(--color-text);
        }

        .container {
            max-width: 960px;
            margin: 0 auto;
            padding: 2rem;
        }

        .header {
            background: linear-gradient(135deg, #333355 0%, #353543 100%);
            color: white;
            padding: 3rem 2rem;
            border-radius: var(--radius-lg);
            margin-bottom: 3rem;
            text-align: center;
            box-shadow: var(--shadow-md);
        }

        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            background: linear-gradient(to right, #fff, #e2e8f0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .type-header {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1.5rem;
            border-radius: var(--radius-base);
            margin: 2rem 0 1rem;
            color: white;
            font-weight: 600;
            font-size: 1.25rem;
            transition: var(--transition);
        }

        .type-header:hover {
            transform: translateX(4px);
            filter: brightness(1.1);
        }

        .scope-tag {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-base);
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--color-text);
            margin: 0.5rem 0;
            transition: var(--transition);
        }

        .scope-tag:hover {
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
            border-color: var(--color-text-secondary);
        }

        .commit-list {
            list-style: none;
            margin: 1rem 0;
        }

        .commit-item {
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-base);
            padding: 1rem;
            margin-bottom: 1rem;
            transition: var(--transition);
        }

        .commit-item:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
            border-color: var(--color-text-secondary);
            background: var(--color-elevated);
        }

        .commit-title {
            font-size: 1rem;
            font-weight: 600;
            color: var(--color-text);
        }

        .commit-meta {
            font-size: 0.875rem;
            color: var(--color-text-secondary);
            margin-top: 0.5rem;
        }

        .commit-body {
            background: var(--color-bg);
            border: 1px solid var(--color-border);
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
    """


class ReportStrategy(ABC):
    @abstractmethod
    def generate(self, commits: Dict) -> str:
        pass

class BaseReportStrategy(ReportStrategy, StyleConfig):
    """Base class combining ReportStrategy with StyleConfig"""
    
    def _generate_style_tag(self) -> str:
        type_colors = '\n'.join([
            f'.type-{type} {{ background: {style["color"]}; }}'
            for type, style in self.TYPE_STYLES.items()
        ])
        return f"<style>{self.BASE_STYLES}\n{type_colors}</style>"

    def _generate_header(self, title: str, subtitle: str) -> List[str]:
        """Generate common header markup"""
        return [
            self._generate_style_tag(),
            "<div class='container'>",
            "<header class='header'>",
            f"<h1>{title}</h1>",
            f"<p>{subtitle}</p>",
            "</header>"
        ]

    def _generate_type_section(self, type_name: str, commits_by_scope: Dict) -> List[str]:
        """Generate markup for a commit type section"""
        if not commits_by_scope:
            return []

        emoji = self.TYPE_STYLES[type_name]["emoji"]
        doc = [
            f'<div class="type-header type-{type_name}">'
            f'{emoji} {type_name.capitalize()}s'
            '</div>'
        ]

        for scope, commits in commits_by_scope.items():
            doc.extend(self._generate_scope_section(scope, commits))
        
        return doc

    def _generate_scope_section(self, scope: str, commits: List[Dict]) -> List[str]:
        """Generate markup for commits under a scope"""
        return [
            "<details open>",
            f"<summary><span class='scope-tag'>{scope}</span></summary>",
            "<ul class='commit-list'>",
            *[self._generate_commit_item(commit) for commit in commits],
            "</ul>",
            "</details>"
        ]

class MarkdownCommitReportGenerator(BaseReportStrategy):
    def _generate_commit_item(self, commit: Dict) -> str:
        """Generate markup for a single commit"""
        elements = [
            "<li class='commit-item'>",
            f"<div class='commit-title'>{commit['title']}</div>",
            f"<div class='commit-meta'>👤 {commit['author']} • 📅 {commit['date']}</div>"
        ]

        if commit['body']:
            elements.extend([
                "<div class='commit-body'>",
                commit['body'],
                "</div>"
            ])

        if commit['refs']:
            elements.append(f"<div class='commit-meta'>🔗 {', '.join(commit['refs'])}</div>")

        elements.append("</li>")
        return '\n'.join(elements)

    def generate(self, commits: Dict) -> str:
        today = datetime.now().strftime("%d %B %Y")
        repo_info = f"{os.getenv('REPO_OWNER')}/{os.getenv('REPO_NAME')}"

        doc = self._generate_header(
            title="📄 Commit Report",
            subtitle=f"Generated on {today}"
        )

        for type_name in self.PRIORITY_ORDER:
            doc.extend(self._generate_type_section(type_name, commits.get(type_name, {})))

        doc.append("</div>")
        return '\n'.join(doc)
    

class ReleaseChangelogStrategy(BaseReportStrategy):
    def _generate_commit_item(self, commit: Dict) -> str:
        """Generate markup for a release commit item"""
        elements = [
            "<li class='commit-item'>",
            f"<div class='commit-title'>{commit['title']}</div>"
        ]

        if commit['refs']:
            elements.append(f"<div class='commit-meta'>🔗 {', '.join(commit['refs'])}</div>")

        elements.append("</li>")
        return '\n'.join(elements)

    def _generate_version_info(self) -> tuple[str, str]:
        """Generate version and date strings"""
        today = datetime.now().strftime("%d %B %Y")
        version = datetime.now().strftime("v%Y.%m.%d")
        return version, today

    def generate(self, commits: Dict) -> str:
        """Generate release changelog HTML"""
        version, today = self._generate_version_info()
        
        # Generate header
        doc = self._generate_header(
            title=f"🚀 Release {version}",
            subtitle=f"Released on {today}"
        )

        # Generate sections for each commit type
        for type_name in self.PRIORITY_ORDER:
            doc.extend(self._generate_type_section(
                type_name, 
                commits.get(type_name, {})
            ))

        doc.append("</div>")
        return '\n'.join(doc)

# class BaseReportStrategy(ReportStrategy, StyleConfig):
#     """Base class combining ReportStrategy with StyleConfig"""
    
#     def _generate_style_tag(self) -> str:
#         type_colors = '\n'.join([
#             f'.type-{type} {{ background: {style["color"]}; }}'
#             for type, style in self.TYPE_STYLES.items()
#         ])
#         return f"<style>{self.BASE_STYLES}\n{type_colors}</style>"

# class MarkdownCommitReportGenerator(BaseReportStrategy):
#     def generate(self, commits: Dict) -> str:
#         today = datetime.now().strftime("%d %B %Y")
#         repo_info = f"{os.getenv('REPO_OWNER')}/{os.getenv('REPO_NAME')}"

#         doc = [
#             self._generate_style_tag(),
#             "<div class='container'>",
#             "<header class='header'>",
#             f"<h1>📄 Commit Report</h1>",
#             f"<p>Generated on {today}</p>",
#             "</header>"
#         ]

#         for type_name in self.PRIORITY_ORDER:
#             if type_name not in commits or not commits[type_name]:
#                 continue

#             emoji = self.TYPE_STYLES[type_name]["emoji"]
#             doc.append(
#                 f'<div class="type-header type-{type_name}">'
#                 f'{emoji} {type_name.capitalize()}s'
#                 '</div>'
#             )

#             for scope, commits_list in commits[type_name].items():
#                 doc.append("<details open>")
#                 doc.append(f"<summary><span class='scope-tag'>{scope}</span></summary>")
#                 doc.append("<ul class='commit-list'>")

#                 for commit in commits_list:
#                     doc.extend([
#                         "<li class='commit-item'>",
#                         f"<div class='commit-title'>{commit['title']}</div>",
#                         f"<div class='commit-meta'>👤 {commit['author']} • 📅 {commit['date']}</div>"
#                     ])

#                     if commit['body']:
#                         doc.extend([
#                             "<div class='commit-body'>",
#                             commit['body'],
#                             "</div>"
#                         ])

#                     if commit['refs']:
#                         doc.append(f"<div class='commit-meta'>🔗 {', '.join(commit['refs'])}</div>")

#                     doc.append("</li>")

#                 doc.extend([
#                     "</ul>",
#                     "</details>"
#                 ])

#         doc.append("</div>")
#         return '\n'.join(doc)

# class ReleaseChangelogStrategy(BaseReportStrategy):
#     def generate(self, commits: Dict) -> str:
#         today = datetime.now().strftime("%d %B %Y")
#         version = datetime.now().strftime("v%Y.%m.%d")

#         doc = [
#             self._generate_style_tag(),
#             "<div class='container'>",
#             "<header class='header'>",
#             f"<h1>🚀 Release {version}</h1>",
#             f"<p>Released on {today}</p>",
#             "</header>"
#         ]

#         for type_name in self.PRIORITY_ORDER:
#             if type_name not in commits or not commits[type_name]:
#                 continue

#             emoji = self.TYPE_STYLES[type_name]["emoji"]
#             doc.append(
#                 f'<div class="type-header type-{type_name}">'
#                 f'{emoji} {type_name.capitalize()}s'
#                 '</div>'
#             )

#             for scope, commits_list in commits[type_name].items():
#                 doc.append("<details open>")
#                 doc.append(f"<summary><span class='scope-tag'>{scope}</span></summary>")
#                 doc.append("<ul class='commit-list'>")

#                 for commit in commits_list:
#                     doc.extend([
#                         "<li class='commit-item'>",
#                         f"<div class='commit-title'>{commit['title']}</div>"
#                     ])

#                     if commit['refs']:
#                         doc.append(f"<div class='commit-meta'>🔗 {', '.join(commit['refs'])}</div>")

#                     doc.append("</li>")

#                 doc.extend([
#                     "</ul>",
#                     "</details>"
#                 ])

#         doc.append("</div>")
#         return '\n'.join(doc)

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