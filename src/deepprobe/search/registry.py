"""
Search source registry and base classes.
搜索源注册表与基类。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum


class SourceType(Enum):
    """Search source types."""
    WEB = "web"
    ENCYCLOPEDIA = "encyclopedia"
    ACADEMIC = "academic"
    CODE = "code"
    NEWS = "news"
    CUSTOM = "custom"


@dataclass
class SearchResult:
    """Represents a single search result."""
    title: str
    url: str
    snippet: str
    source: str
    source_type: SourceType = SourceType.WEB
    relevance_score: float = 0.0
    published_date: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    fetched_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source,
            "source_type": self.source_type.value,
            "relevance_score": self.relevance_score,
            "published_date": self.published_date,
            "author": self.author,
            "tags": self.tags,
            "fetched_at": self.fetched_at,
        }


class BaseSearchSource(ABC):
    """Abstract base class for search sources."""

    name: str = "base"
    source_type: SourceType = SourceType.WEB
    description: str = ""
    requires_api_key: bool = False

    @abstractmethod
    def search(self, query: str, max_results: int = 10, **kwargs) -> List[SearchResult]:
        """Execute a search query.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return.
            **kwargs: Additional source-specific parameters.

        Returns:
            List of SearchResult objects.
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this search source is available."""
        ...

    def validate_config(self, config: dict) -> bool:
        """Validate source-specific configuration."""
        return True


class SourceRegistry:
    """Registry for managing search sources."""

    def __init__(self):
        self._sources: dict[str, BaseSearchSource] = {}

    def register(self, source: BaseSearchSource) -> None:
        """Register a search source."""
        self._sources[source.name] = source

    def get(self, name: str) -> Optional[BaseSearchSource]:
        """Get a registered search source by name."""
        return self._sources.get(name)

    def get_available(self) -> List[BaseSearchSource]:
        """Get all available (ready-to-use) search sources."""
        return [s for s in self._sources.values() if s.is_available()]

    def get_all(self) -> List[BaseSearchSource]:
        """Get all registered search sources."""
        return list(self._sources.values())

    def list_sources(self) -> None:
        """Print all available sources in a formatted table."""
        sources = self.get_all()
        if not sources:
            print("⚠️  No search sources registered. / 未注册搜索源。")
            return

        print("\n🔍 Available Search Sources / 可用搜索源:")
        print("=" * 72)
        print(f"  {'Name':<16} {'Type':<14} {'Status':<10} {'Description'}")
        print("-" * 72)
        for s in sources:
            available = s.is_available()
            status = "✅ Ready" if available else "❌ Unavailable"
            desc = s.description[:30] + "..." if len(s.description) > 30 else s.description
            print(f"  {s.name:<16} {s.source_type.value:<14} {status:<10} {desc}")
        print("=" * 72)
        print(f"  Total: {len(sources)} sources, {len(self.get_available())} available")
        print()

    def auto_register(self) -> None:
        """Auto-discover and register built-in search sources."""
        try:
            from deepprobe.search.sources.duckduckgo_source import DuckDuckGoSource
            self.register(DuckDuckGoSource())
        except ImportError:
            pass

        try:
            from deepprobe.search.sources.wikipedia_source import WikipediaSource
            self.register(WikipediaSource())
        except ImportError:
            pass

        try:
            from deepprobe.search.sources.github_source import GitHubSource
            self.register(GitHubSource())
        except ImportError:
            pass

        try:
            from deepprobe.search.sources.arxiv_source import ArxivSource
            self.register(ArxivSource())
        except ImportError:
            pass

        try:
            from deepprobe.search.sources.news_source import NewsAggregatorSource
            self.register(NewsAggregatorSource())
        except ImportError:
            pass
