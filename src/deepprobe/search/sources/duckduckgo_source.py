"""
DuckDuckGo search source implementation.
DuckDuckGo搜索源实现。
"""

import json
import urllib.parse
import urllib.request
from typing import List, Optional

from ..registry import BaseSearchSource, SearchResult, SourceType


class DuckDuckGoSource(BaseSearchSource):
    """DuckDuckGo search source using the lite/html API."""

    name = "duckduckgo"
    source_type = SourceType.WEB
    description = "DuckDuckGo web search - privacy-friendly, no tracking"
    requires_api_key = False

    def __init__(self, timeout: int = 30):
        self._timeout = timeout

    def search(self, query: str, max_results: int = 10, **kwargs) -> List[SearchResult]:
        """Search DuckDuckGo for web results."""
        results = []
        try:
            results = self._search_lite(query, max_results)
        except Exception:
            # Fallback to HTML scraping
            try:
                results = self._search_html(query, max_results)
            except Exception:
                pass

        # Score results by relevance
        query_lower = query.lower()
        query_terms = set(query_lower.split())

        for result in results:
            title_lower = result.title.lower()
            snippet_lower = result.snippet.lower()
            combined = title_lower + " " + snippet_lower
            matching_terms = sum(1 for term in query_terms if term in combined)
            result.relevance_score = min(1.0, matching_terms / max(len(query_terms), 1))

        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results[:max_results]

    def _search_lite(self, query: str, max_results: int) -> List[SearchResult]:
        """Search using DuckDuckGo lite endpoint."""
        encoded_query = urllib.parse.urlencode({"q": query})
        url = f"https://lite.duckduckgo.com/lite/?{encoded_query}"

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )

        with urllib.request.urlopen(req, timeout=self._timeout) as response:
            html = response.read().decode("utf-8", errors="ignore")

        return self._parse_lite_html(html, max_results)

    def _parse_lite_html(self, html: str, max_results: int) -> List[SearchResult]:
        """Parse DuckDuckGo lite HTML response."""
        results = []

        # Split by result link elements
        import re

        # Find all link-result pairs in the lite HTML
        link_pattern = re.compile(
            r'<a[^>]+rel="nofollow"[^>]+href="([^"]+)"[^>]*>(.*?)</a>.*?'
            r'<td[^>]*class="result-snippet"[^>]*>(.*?)</td>',
            re.DOTALL | re.IGNORECASE,
        )

        # Alternative pattern for lite version
        alt_pattern = re.compile(
            r'<a[^>]+href="(https?://[^"]+)"[^>]*class="result-link"[^>]*>(.*?)</a>'
            r'.*?<td[^>]*>(.*?)</td>',
            re.DOTALL | re.IGNORECASE,
        )

        # Generic pattern
        generic_pattern = re.compile(
            r'<a[^>]+href="(https?://[^"]+)"[^>]*>([^<]+)</a>'
            r'.*?<td[^>]*>(.*?)</td>',
            re.DOTALL | re.IGNORECASE,
        )

        for pattern in [link_pattern, alt_pattern, generic_pattern]:
            matches = pattern.findall(html)
            if matches:
                for url, title, snippet in matches[:max_results]:
                    # Clean HTML tags
                    title = re.sub(r"<[^>]+>", "", title).strip()
                    snippet = re.sub(r"<[^>]+>", "", snippet).strip()

                    # Skip DuckDuckGo internal links
                    if "duckduckgo.com" in url and "/l/" in url:
                        continue

                    if title and snippet and len(title) > 3:
                        results.append(SearchResult(
                            title=title[:200],
                            url=url[:500],
                            snippet=snippet[:500],
                            source=self.name,
                            source_type=self.source_type,
                        ))
                break

        return results

    def _search_html(self, query: str, max_results: int) -> List[SearchResult]:
        """Search using DuckDuckGo HTML endpoint as fallback."""
        encoded_query = urllib.parse.urlencode({"q": query})
        url = f"https://html.duckduckgo.com/html/?{encoded_query}"

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html",
            },
        )

        with urllib.request.urlopen(req, timeout=self._timeout) as response:
            html = response.read().decode("utf-8", errors="ignore")

        results = []
        import re

        # Parse HTML results
        result_pattern = re.compile(
            r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>.*?'
            r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>',
            re.DOTALL | re.IGNORECASE,
        )

        for url, title, snippet in result_pattern.findall(html)[:max_results]:
            title = re.sub(r"<[^>]+>", "", title).strip()
            snippet = re.sub(r"<[^>]+>", "", snippet).strip()
            if title and snippet:
                results.append(SearchResult(
                    title=title[:200],
                    url=url[:500],
                    snippet=snippet[:500],
                    source=self.name,
                    source_type=self.source_type,
                ))

        return results

    def is_available(self) -> bool:
        """Check if DuckDuckGo is accessible."""
        try:
            req = urllib.request.Request(
                "https://lite.duckduckgo.com/",
                headers={"User-Agent": "DeepProbe/1.0"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except Exception:
            return False
