"""
Wikipedia search source implementation.
Wikipedia搜索源实现。
"""

import json
import urllib.parse
import urllib.request
from typing import List, Optional

from ..registry import BaseSearchSource, SearchResult, SourceType


class WikipediaSource(BaseSearchSource):
    """Wikipedia search source using the MediaWiki API."""

    name = "wikipedia"
    source_type = SourceType.ENCYCLOPEDIA
    description = "Wikipedia encyclopedia - comprehensive knowledge base"
    requires_api_key = False

    def __init__(self, language: str = "en", timeout: int = 30):
        self._language = language
        self._timeout = timeout
        self._api_base = f"https://{language}.wikipedia.org/w/api.php"

    def search(self, query: str, max_results: int = 10, **kwargs) -> List[SearchResult]:
        """Search Wikipedia for articles."""
        language = kwargs.get("language", self._language)
        api_base = f"https://{language}.wikipedia.org/w/api.php"

        results = []

        # Step 1: Search for article titles
        search_params = urllib.parse.urlencode({
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": min(max_results, 50),
            "format": "json",
            "utf8": "1",
        })

        url = f"{api_base}?{search_params}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "DeepProbe/1.0 (Research Bot)"},
        )

        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception:
            return results

        search_results = data.get("query", {}).get("search", [])
        if not search_results:
            return results

        # Step 2: Get extracts for top results
        titles = [r["title"] for r in search_results[:max_results]]
        extract_params = urllib.parse.urlencode({
            "action": "query",
            "titles": "|".join(titles),
            "prop": "extracts|info",
            "exintro": "1",
            "explaintext": "1",
            "exsentences": "5",
            "inprop": "url",
            "format": "json",
            "utf8": "1",
        })

        url = f"{api_base}?{extract_params}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "DeepProbe/1.0 (Research Bot)"},
        )

        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                extract_data = json.loads(resp.read().decode("utf-8"))
        except Exception:
            # Fallback: use search snippets
            for r in search_results[:max_results]:
                article_url = f"https://{language}.wikipedia.org/wiki/{urllib.parse.quote(r['title'].replace(' ', '_'))}"
                results.append(SearchResult(
                    title=r["title"],
                    url=article_url,
                    snippet=r.get("snippet", "").replace("<span class=\"searchmatch\">", "").replace("</span>", ""),
                    source=self.name,
                    source_type=self.source_type,
                    relevance_score=r.get("wordcount", 0) / 1000.0,
                ))
            return results

        # Parse extracts
        pages = extract_data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if page_id == "-1":
                continue

            title = page_data.get("title", "")
            extract = page_data.get("extract", "")
            full_url = page_data.get("fullurl", "")
            word_count = page_data.get("length", 0)

            if title and extract:
                # Calculate relevance based on word count and query match
                query_lower = query.lower()
                relevance = 0.0
                if query_lower in title.lower():
                    relevance += 0.5
                relevance += min(0.5, word_count / 20000.0)

                results.append(SearchResult(
                    title=title,
                    url=full_url,
                    snippet=extract[:500],
                    source=self.name,
                    source_type=self.source_type,
                    relevance_score=relevance,
                ))

        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results[:max_results]

    def is_available(self) -> bool:
        """Check if Wikipedia API is accessible."""
        try:
            params = urllib.parse.urlencode({
                "action": "query",
                "list": "search",
                "srsearch": "test",
                "srlimit": "1",
                "format": "json",
            })
            url = f"{self._api_base}?{params}"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "DeepProbe/1.0"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except Exception:
            return False
