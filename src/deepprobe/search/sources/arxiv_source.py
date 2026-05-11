"""
arXiv search source implementation.
arXiv学术搜索源实现。
"""

import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import List

from ..registry import BaseSearchSource, SearchResult, SourceType


class ArxivSource(BaseSearchSource):
    """arXiv academic paper search source."""

    name = "arxiv"
    source_type = SourceType.ACADEMIC
    description = "arXiv - open access academic papers"
    requires_api_key = False

    def __init__(self, timeout: int = 30):
        self._timeout = timeout
        self._api_base = "http://export.arxiv.org/api/query"

    def search(self, query: str, max_results: int = 10, **kwargs) -> List[SearchResult]:
        """Search arXiv for academic papers."""
        search_field = kwargs.get("field", "all")
        sort_by = kwargs.get("sort", "relevance")

        params = urllib.parse.urlencode({
            "search_query": f"{search_field}:{query}",
            "start": "0",
            "max_results": str(min(max_results, 30)),
            "sortBy": sort_by,
            "sortOrder": "descending",
        })

        url = f"{self._api_base}?{params}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "DeepProbe/1.0 (Research Bot)"},
        )

        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                xml_data = resp.read().decode("utf-8")
        except Exception:
            return []

        return self._parse_atom(xml_data, max_results)

    def _parse_atom(self, xml_data: str, max_results: int) -> List[SearchResult]:
        """Parse arXiv Atom XML response."""
        results = []

        # Register arXiv namespace
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom",
        }

        try:
            root = ET.fromstring(xml_data)
        except ET.ParseError:
            return []

        entries = root.findall("atom:entry", ns)

        for entry in entries[:max_results]:
            # Extract title
            title_elem = entry.find("atom:title", ns)
            title = self._clean_text(title_elem.text if title_elem is not None else "")

            # Extract summary
            summary_elem = entry.find("atom:summary", ns)
            summary = self._clean_text(summary_elem.text if summary_elem is not None else "")

            # Extract link (PDF preferred)
            pdf_url = ""
            abs_url = ""
            for link in entry.findall("atom:link", ns):
                href = link.get("href", "")
                title_attr = link.get("title", "")
                rel = link.get("rel", "")
                if title_attr == "pdf":
                    pdf_url = href
                elif rel == "alternate":
                    abs_url = href

            display_url = pdf_url or abs_url

            # Extract authors
            authors = []
            for author in entry.findall("atom:author", ns):
                name_elem = author.find("atom:name", ns)
                if name_elem is not None:
                    authors.append(name_elem.text)

            # Extract categories
            categories = []
            for cat in entry.findall("atom:category", ns):
                term = cat.get("term", "")
                if term:
                    categories.append(term)

            # Extract published date
            published_elem = entry.find("atom:published", ns)
            published = published_elem.text[:10] if published_elem is not None else ""

            # Build snippet
            snippet_parts = [summary[:300]]
            if authors:
                author_str = ", ".join(authors[:3])
                if len(authors) > 3:
                    author_str += f" et al. ({len(authors)} authors)"
                snippet_parts.append(f"Authors: {author_str}")
            if categories:
                snippet_parts.append(f"Categories: {', '.join(categories[:3])}")
            if pdf_url:
                snippet_parts.append(f"PDF: {pdf_url}")

            results.append(SearchResult(
                title=title,
                url=display_url,
                snippet=" | ".join(snippet_parts),
                source=self.name,
                source_type=self.source_type,
                published_date=published,
                author=", ".join(authors[:3]),
                tags=categories,
                relevance_score=0.5,  # Default score, arXiv sorts by relevance
            ))

        return results

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean whitespace from text."""
        if not text:
            return ""
        return re.sub(r"\s+", " ", text).strip()

    def is_available(self) -> bool:
        """Check if arXiv API is accessible."""
        try:
            url = f"{self._api_base}?search_query=test&max_results=1"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "DeepProbe/1.0"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except Exception:
            return False
