
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass

@dataclass
class CommitInfo:
    """Data class to hold parsed commit information"""
    type: str
    scope: str
    title: str
    body: str
    refs: List[str]
    author: str
    date: str
