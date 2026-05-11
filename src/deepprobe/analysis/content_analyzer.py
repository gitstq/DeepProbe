"""
Content analysis engine.
内容分析引擎。
"""

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

from ..search.registry import SearchResult


@dataclass
class AnalysisResult:
    """Result of content analysis."""
    keywords: List[Tuple[str, float]] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    sentiment_score: float = 0.0  # -1.0 to 1.0
    summary: str = ""
    key_findings: List[str] = field(default_factory=list)
    entity_mentions: Dict[str, int] = field(default_factory=dict)
    source_distribution: Dict[str, int] = field(default_factory=dict)
    quality_score: float = 0.0  # 0.0 to 1.0
    coverage_score: float = 0.0  # 0.0 to 1.0


class ContentAnalyzer:
    """Analyzes search results to extract insights."""

    # Common stop words to filter out
    STOP_WORDS = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "dare", "ought",
        "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
        "as", "into", "through", "during", "before", "after", "above", "below",
        "between", "out", "off", "over", "under", "again", "further", "then",
        "once", "here", "there", "when", "where", "why", "how", "all", "both",
        "each", "few", "more", "most", "other", "some", "such", "no", "nor",
        "not", "only", "own", "same", "so", "than", "too", "very", "just",
        "because", "but", "and", "or", "if", "while", "about", "up", "it",
        "its", "this", "that", "these", "those", "i", "me", "my", "we",
        "our", "you", "your", "he", "him", "his", "she", "her", "they",
        "them", "their", "what", "which", "who", "whom", "whose",
        # Chinese stop words
        "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都",
        "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会",
        "着", "没有", "看", "好", "自己", "这",
    }

    # Sentiment word lists
    POSITIVE_WORDS = {
        "good", "great", "excellent", "amazing", "innovative", "breakthrough",
        "success", "improve", "benefit", "advantage", "efficient", "powerful",
        "revolutionary", "promising", "significant", "remarkable", "outstanding",
        "cutting-edge", "state-of-the-art", "leading", "pioneering",
        "好", "优秀", "创新", "突破", "成功", "提升", "优势", "高效", "强大",
    }

    NEGATIVE_WORDS = {
        "bad", "poor", "fail", "failure", "problem", "issue", "risk", "threat",
        "concern", "challenge", "difficult", "complex", "limit", "restrict",
        "decline", "worse", "dangerous", "vulnerable", "weakness",
        "差", "失败", "问题", "风险", "威胁", "挑战", "困难", "复杂", "限制",
    }

    def analyze(self, results: List[SearchResult], query: str = "") -> AnalysisResult:
        """Perform comprehensive analysis on search results.

        Args:
            results: List of search results to analyze.
            query: Original research query for context.

        Returns:
            AnalysisResult with extracted insights.
        """
        if not results:
            return AnalysisResult(summary="No results to analyze.")

        analysis = AnalysisResult()

        # 1. Extract keywords using TF-IDF-like scoring
        analysis.keywords = self._extract_keywords(results, query)

        # 2. Identify themes
        analysis.themes = self._identify_themes(results, query)

        # 3. Analyze sentiment
        analysis.sentiment_score = self._analyze_sentiment(results)

        # 4. Generate summary
        analysis.summary = self._generate_summary(results, query, analysis)

        # 5. Extract key findings
        analysis.key_findings = self._extract_key_findings(results, query)

        # 6. Extract entity mentions
        analysis.entity_mentions = self._extract_entities(results)

        # 7. Analyze source distribution
        analysis.source_distribution = self._analyze_sources(results)

        # 8. Calculate quality score
        analysis.quality_score = self._calculate_quality(results)

        # 9. Calculate coverage score
        analysis.coverage_score = self._calculate_coverage(results, query)

        return analysis

    def _extract_keywords(
        self, results: List[SearchResult], query: str
    ) -> List[Tuple[str, float]]:
        """Extract and rank keywords from results."""
        word_freq = Counter()
        doc_freq = Counter()

        query_terms = set(query.lower().split())

        for result in results:
            text = (result.title + " " + result.snippet).lower()
            words = re.findall(r"[a-z\u4e00-\u9fff]{2,}", text)

            seen = set()
            for word in words:
                if word not in self.STOP_WORDS and word not in query_terms:
                    word_freq[word] += 1
                    if word not in seen:
                        doc_freq[word] += 1
                        seen.add(word)

        total_docs = len(results)

        # TF-IDF-like scoring
        keyword_scores = []
        for word, freq in word_freq.most_common(50):
            if freq >= 2:
                tf = freq / max(word_freq.values())
                idf = total_docs / max(doc_freq[word], 1)
                score = tf * (idf / total_docs)
                keyword_scores.append((word, round(score, 4)))

        keyword_scores.sort(key=lambda x: x[1], reverse=True)
        return keyword_scores[:20]

    def _identify_themes(
        self, results: List[SearchResult], query: str
    ) -> List[str]:
        """Identify major themes from results."""
        themes = []
        query_lower = query.lower()

        # Group results by common patterns
        topic_groups: Dict[str, List[str]] = {}

        for result in results:
            text = (result.title + " " + result.snippet).lower()
            # Extract potential theme indicators
            for keyword, score in self._extract_keywords([result], "")[:3]:
                if keyword not in topic_groups:
                    topic_groups[keyword] = []
                topic_groups[keyword].append(result.title)

        # Select themes with multiple supporting results
        for keyword, titles in sorted(
            topic_groups.items(), key=lambda x: len(x[1]), reverse=True
        )[:8]:
            if len(titles) >= 2:
                themes.append(f"{keyword} ({len(titles)} mentions)")

        return themes[:6]

    def _analyze_sentiment(self, results: List[SearchResult]) -> float:
        """Analyze overall sentiment of results."""
        total_score = 0.0
        total_words = 0

        for result in results:
            text = (result.title + " " + result.snippet).lower()
            words = re.findall(r"[a-z\u4e00-\u9fff]+", text)

            for word in words:
                if word in self.POSITIVE_WORDS:
                    total_score += 1.0
                elif word in self.NEGATIVE_WORDS:
                    total_score -= 1.0
                total_words += 1

        if total_words == 0:
            return 0.0

        return max(-1.0, min(1.0, total_score / total_words * 10))

    def _generate_summary(
        self,
        results: List[SearchResult],
        query: str,
        analysis: "AnalysisResult",
    ) -> str:
        """Generate a concise summary of findings."""
        top_keywords = [kw for kw, _ in analysis.keywords[:5]]
        keyword_str = ", ".join(top_keywords) if top_keywords else "various topics"

        source_count = len(set(r.source for r in results))

        sentiment_desc = "positive" if analysis.sentiment_score > 0.2 else \
                        "negative" if analysis.sentiment_score < -0.2 else "neutral"

        summary = (
            f"Based on analysis of {len(results)} results from {source_count} source(s), "
            f"the research on '{query}' reveals key themes around {keyword_str}. "
            f"The overall sentiment is {sentiment_desc} "
            f"(score: {analysis.sentiment_score:.2f}). "
            f"Data quality score: {analysis.quality_score:.2f}, "
            f"coverage score: {analysis.coverage_score:.2f}."
        )

        return summary

    def _extract_key_findings(
        self, results: List[SearchResult], query: str
    ) -> List[str]:
        """Extract key findings from top results."""
        findings = []

        for i, result in enumerate(results[:5]):
            if result.snippet:
                # Truncate to a reasonable length
                snippet = result.snippet[:200]
                if len(result.snippet) > 200:
                    snippet += "..."
                findings.append(f"[{result.source}] {snippet}")

        return findings

    def _extract_entities(self, results: List[SearchResult]) -> Dict[str, int]:
        """Extract named entities from results."""
        entities = Counter()

        for result in results:
            text = result.title + " " + result.snippet

            # Extract capitalized words (potential named entities)
            capitalized = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text)
            for entity in capitalized:
                if len(entity) > 2 and entity.lower() not in self.STOP_WORDS:
                    entities[entity] += 1

            # Extract author names
            if result.author:
                entities[result.author] += 1

        return dict(entities.most_common(15))

    def _analyze_sources(self, results: List[SearchResult]) -> Dict[str, int]:
        """Analyze the distribution of sources."""
        return dict(Counter(r.source for r in results))

    def _calculate_quality(self, results: List[SearchResult]) -> float:
        """Calculate overall quality score of results."""
        if not results:
            return 0.0

        scores = []
        for result in results:
            score = 0.0

            # Has meaningful title
            if len(result.title) > 10:
                score += 0.2

            # Has meaningful snippet
            if len(result.snippet) > 50:
                score += 0.3

            # Has relevance score
            score += result.relevance_score * 0.3

            # Has metadata
            if result.author or result.published_date:
                score += 0.1

            # Has tags
            if result.tags:
                score += 0.1

            scores.append(min(1.0, score))

        return sum(scores) / len(scores)

    def _calculate_coverage(
        self, results: List[SearchResult], query: str
    ) -> float:
        """Calculate how well the results cover the query topic."""
        if not results:
            return 0.0

        query_terms = set(query.lower().split())
        covered_terms = set()

        for result in results:
            text = (result.title + " " + result.snippet).lower()
            for term in query_terms:
                if term in text:
                    covered_terms.add(term)

        if not query_terms:
            return 0.5

        return len(covered_terms) / len(query_terms)
