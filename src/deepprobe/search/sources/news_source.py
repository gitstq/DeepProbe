"""
News aggregator search source implementation.
新闻聚合搜索源实现。
"""

import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from typing import List

from ..registry import BaseSearchSource, SearchResult, SourceType


class NewsAggregatorSource(BaseSearchSource):
    """News aggregator using multiple public RSS/Atom feeds."""

    name = "news"
    source_type = SourceType.NEWS
    description = "News aggregator - tech news from multiple feeds"
    requires_api_key = False

    # Public tech news feeds (no API key required)
    FEEDS = {
        "hackernews": {
            "url": "https://hacker-news.firebaseio.com/v0/",
            "type": "hn_api",
            "description": "Hacker News - tech news",
        },
        "github_trending": {
            "url": "https://api.github.com/search/repositories",
            "type": "github_trending",
            "description": "GitHub Trending - popular repos",
        },
    }

    def __init__(self, timeout: int = 30):
        self._timeout = timeout

    def search(self, query: str, max_results: int = 10, **kwargs) -> List[SearchResult]:
        """Search news sources for articles."""
        results = []

        # Search Hacker News
        try:
            hn_results = self._search_hackernews(query, max_results)
            results.extend(hn_results)
        except Exception:
            pass

        # Search via DuckDuckGo news
        try:
            news_results = self._search_ddg_news(query, max_results)
            results.extend(news_results)
        except Exception:
            pass

        # Score and sort
        query_lower = query.lower()
        query_terms = set(query_lower.split())

        for result in results:
            combined = (result.title + " " + result.snippet).lower()
            matching = sum(1 for t in query_terms if t in combined)
            result.relevance_score = min(1.0, matching / max(len(query_terms), 1))

        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results[:max_results]

    def _search_hackernews(self, query: str, max_results: int) -> List[SearchResult]:
        """Search Hacker News via Algolia API."""
        params = urllib.parse.urlencode({
            "query": query,
            "tags": "story",
            "hitsPerPage": str(min(max_results, 20)),
        })

        url = f"https://hn.algolia.com/api/v1/search?{params}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "DeepProbe/1.0"},
        )

        with urllib.request.urlopen(req, timeout=self._timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        results = []
        for hit in data.get("hits", [])[:max_results]:
            title = hit.get("title", "")
            url = hit.get("url", "") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
            points = hit.get("points", 0)
            num_comments = hit.get("num_comments", 0)
            author = hit.get("author", "")
            created = hit.get("created_at", "")[:10]

            snippet_parts = [hit.get("story_text", "") or title]
            snippet_parts.append(f"▲ {points} | 💬 {num_comments}")
            if author:
                snippet_parts.append(f"by {author}")

            results.append(SearchResult(
                title=title,
                url=url,
                snippet=" | ".join(snippet_parts)[:500],
                source="hackernews",
                source_type=self.source_type,
                published_date=created,
                author=author,
                relevance_score=min(1.0, points / 500.0),
            ))

        return results

    def _search_ddg_news(self, query: str, max_results: int) -> List[SearchResult]:
        """Search DuckDuckGo for news results."""
        encoded_query = urllib.parse.urlencode({"q": f"{query} news"})
        url = f"https://html.duckduckgo.com/html/?{encoded_query}"

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                "Accept": "text/html",
            },
        )

        with urllib.request.urlopen(req, timeout=self._timeout) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        results = []
        pattern = re.compile(
            r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>.*?'
            r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>',
            re.DOTALL | re.IGNORECASE,
        )

        for url, title, snippet in pattern.findall(html)[:max_results]:
            title = re.sub(r"<[^>]+>", "", title).strip()
            snippet = re.sub(r"<[^>]+>", "", snippet).strip()
            if title and snippet:
                results.append(SearchResult(
                    title=title[:200],
                    url=url[:500],
                    snippet=snippet[:500],
                    source="news_web",
                    source_type=self.source_type,
                ))

        return results

    def is_available(self) -> bool:
        """Check if news sources are accessible."""
        try:
            url = "https://hn.algolia.com/api/v1/search?query=test&hitsPerPage=1"
            req = urllib.request.Request(url, headers={"User-Agent": "DeepProbe/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except Exception:
            return False
