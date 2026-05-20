"""
Data models for the CodeScribe scraping engine.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class RepositoryMetadata:
    """Metadata representing an open-source repository."""
    platform: str  # "github" or "gitlab"
    id: str
    owner: str
    name: str
    full_name: str
    url: str
    description: Optional[str] = None
    language: Optional[str] = None
    stars: int = 0
    forks: int = 0
    default_branch: str = "main"
    topics: List[str] = field(default_factory=list)
    license: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for JSON serialization."""
        return {
            "platform": self.platform,
            "id": self.id,
            "owner": self.owner,
            "name": self.name,
            "full_name": self.full_name,
            "url": self.url,
            "description": self.description,
            "language": self.language,
            "stars": self.stars,
            "forks": self.forks,
            "default_branch": self.default_branch,
            "topics": self.topics,
            "license": self.license,
            "updated_at": self.updated_at,
        }
