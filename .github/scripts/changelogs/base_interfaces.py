from abc import ABC, abstractmethod
from typing import Dict, Optional, List

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
    def generate(
        self, 
        commits: Dict,
        current_tag: Optional[str] = None,
        previous_tag: Optional[str] = None
    ) -> str:
        pass