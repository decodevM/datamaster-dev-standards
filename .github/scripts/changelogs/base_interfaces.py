from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Union, Tuple

from git import Tag, Commit


# Base classes and interfaces
class CommitFetcher(ABC):
    @abstractmethod
    def fetch_commits(self, branch="main") -> List[Dict]:
        """Fetch all commits from repository"""
        pass

    @abstractmethod
    def get_tags(self) -> Tuple[Optional[str], Optional[str]]:
        """Get latest and previous tags if available"""
        pass

    @abstractmethod
    def get_commits_between_refs(
        self,
        base_ref: Union[Tag, Commit],
        head_ref: Union[Tag, Commit]
    ) -> List[Dict]:
        """Get commits between two refs (tags or commits)"""
        pass

    @abstractmethod
    def get_commit_from_tag(self, tag: str) -> Commit:
        """Get commit object from tag name"""
        pass

class CommitParser(ABC):
    @abstractmethod
    def parse(self, message: str) -> Optional[Dict]:
        pass

class ReportStrategy(ABC):
    @abstractmethod
    def generate(
        self, 
        commits: Dict,
        current_tag: Optional[str] = None,
        previous_tag: Optional[str] = None
    ) -> str:
        pass