from base_interfaces import CommitFetcher, CommitParser
from commit_info import CommitInfo
from basic_commit_parser import BasicCommitParser
from datetime import datetime
from typing import Dict, List, Set, Tuple

class CommitDocumentManager:
    def __init__(self, commit_fetcher: CommitFetcher, commit_parser: CommitParser):
        self.commit_fetcher = commit_fetcher
        self.commit_parser = commit_parser

    def _parse_commit_date(self, date_str: str) -> str:
        """Format commit date string"""
        return datetime.strptime(
            date_str, 
            "%Y-%m-%dT%H:%M:%SZ"
        ).strftime("%d %B %Y %H:%M")

    def _create_commit_info(self, commit: Dict, parsed: Dict) -> CommitInfo:
        """Create CommitInfo from raw commit and parsed data"""
        return CommitInfo(
            type=parsed["type"],
            scope=parsed["scope"],
            title=parsed["title"],
            body=parsed["body"] or "",
            refs=parsed["refs"],
            author=commit["commit"]["author"]["name"],
            date=self._parse_commit_date(commit["commit"]["author"]["date"])
        )

    def _get_commit_id(self, info: CommitInfo) -> Tuple:
        """Create unique identifier for commit"""
        return (
            info.type,
            info.scope,
            info.title,
            info.body,
            tuple(info.refs)
        )

    def _add_to_categories(
        self, 
        categorized: Dict, 
        info: CommitInfo
    ) -> None:
        """Add commit info to categorized dictionary"""
        if info.scope not in categorized[info.type]:
            categorized[info.type][info.scope] = []
            
        categorized[info.type][info.scope].append({
            "title": info.title,
            "body": info.body,
            "author": info.author,
            "date": info.date,
            "refs": info.refs
        })

    def categorize_commits(self, commits: List[Dict]) -> Dict:
        """Categorize commits by type and scope"""
        categorized = {t: {} for t in BasicCommitParser.TYPES}
        seen: Set[Tuple] = set()

        for commit in commits:
            # Parse commit message
            parsed = self.commit_parser.parse(commit["commit"]["message"])
            if not parsed:
                continue

            # Create commit info object
            commit_info = self._create_commit_info(commit, parsed)
            commit_id = self._get_commit_id(commit_info)

            # Skip if already processed
            if commit_id in seen:
                continue

            # Add to categories and mark as seen
            seen.add(commit_id)
            self._add_to_categories(categorized, commit_info)

        return categorized
   