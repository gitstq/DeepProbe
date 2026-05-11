"""
GitHub search source implementation.
GitHub搜索源实现。
"""

import json
import urllib.parse
import urllib.request
from typing import List, Optional

from ..registry import BaseSearchSource, SearchResult, SourceType


class GitHubSource(BaseSearchSource):
    """GitHub repository search source using the public API."""

    name = "github"
    source_type = SourceType.CODE
    description = "GitHub repositories - open source code search"
    requires_api_key = False

    def __init__(self, token: str = "", timeout: int = 30):
        self._token = token
        self._timeout = timeout
        self._api_base = "https://api.github.com"

    def search(self, query: str, max_results: int = 10, **kwargs) -> List[SearchResult]:
        """Search GitHub for repositories."""
        sort = kwargs.get("sort", "stars")
        order = kwargs.get("order", "desc")

        params = urllib.parse.urlencode({
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": min(max_results, 30),
        })

        url = f"{self._api_base}/search/repositories?{params}"
        headers = {
            "User-Agent": "DeepProbe/1.0 (Research Bot)",
            "Accept": "application/vnd.github.v3+json",
        }
        if self._token:
            headers["Authorization"] = f"token {self._token}"

        req = urllib.request.Request(url, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception:
            return []

        results = []
        items = data.get("items", [])

        for item in items[:max_results]:
            stars = item.get("stargazers_count", 0)
            forks = item.get("forks_count", 0)
            lang = item.get("language", "")
            description = item.get("description", "") or ""
            updated = item.get("updated_at", "")
            topics = item.get("topics", [])

            # Build rich snippet
            snippet_parts = [description]
            if lang:
                snippet_parts.append(f"Language: {lang}")
            snippet_parts.append(f"⭐ {stars:,} | 🍴 {forks:,}")
            if updated:
                snippet_parts.append(f"Updated: {updated[:10]}")
            if topics:
                snippet_parts.append(f"Topics: {', '.join(topics[:5])}")

            # Relevance score based on stars and freshness
            relevance = min(1.0, (stars / 10000.0) * 0.7 + 0.3)

            results.append(SearchResult(
                title=item.get("full_name", item.get("name", "")),
                url=item.get("html_url", ""),
                snippet=" | ".join(snippet_parts),
                source=self.name,
                source_type=self.source_type,
                relevance_score=relevance,
                author=item.get("owner", {}).get("login", ""),
                published_date=item.get("created_at", ""),
                tags=topics,
            ))

        return results

    def is_available(self) -> bool:
        """Check if GitHub API is accessible."""
        try:
            url = f"{self._api_base}/rate_limit"
            headers = {"User-Agent": "DeepProbe/1.0"}
            if self._token:
                headers["Authorization"] = f"token {self._token}"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except Exception:
            return False
