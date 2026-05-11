"""
Unit tests for DeepProbe core modules.
DeepProbe核心模块单元测试。
"""

import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from deepprobe.search.registry import (
    BaseSearchSource, SearchResult, SourceType, SourceRegistry,
)
from deepprobe.analysis.content_analyzer import ContentAnalyzer
from deepprobe.report.generator import ReportGenerator, ResearchReport
from deepprobe.storage.engine import StorageEngine
from deepprobe.core.config import ConfigManager


class TestSearchResult(unittest.TestCase):
    """Test SearchResult dataclass."""

    def test_create_result(self):
        result = SearchResult(
            title="Test Title",
            url="https://example.com",
            snippet="Test snippet",
            source="test",
        )
        self.assertEqual(result.title, "Test Title")
        self.assertEqual(result.source, "test")
        self.assertEqual(result.source_type, SourceType.WEB)
        self.assertEqual(result.relevance_score, 0.0)

    def test_to_dict(self):
        result = SearchResult(
            title="Test",
            url="https://example.com",
            snippet="Snippet",
            source="test",
            tags=["tag1", "tag2"],
        )
        d = result.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d["title"], "Test")
        self.assertEqual(d["tags"], ["tag1", "tag2"])
        self.assertIn("fetched_at", d)


class TestContentAnalyzer(unittest.TestCase):
    """Test ContentAnalyzer."""

    def setUp(self):
        self.analyzer = ContentAnalyzer()

    def test_empty_results(self):
        result = self.analyzer.analyze([], "test query")
        self.assertEqual(result.summary, "No results to analyze.")
        self.assertEqual(result.keywords, [])
        self.assertEqual(result.quality_score, 0.0)

    def test_keyword_extraction(self):
        results = [
            SearchResult(
                title="Python Machine Learning Tutorial",
                url="https://example.com/1",
                snippet="Learn about machine learning algorithms and neural networks",
                source="test",
            ),
            SearchResult(
                title="Python Data Science Guide",
                url="https://example.com/2",
                snippet="Data science with Python pandas and numpy libraries",
                source="test",
            ),
            SearchResult(
                title="Machine Learning Applications",
                url="https://example.com/3",
                snippet="Machine learning is used in many applications",
                source="test",
            ),
        ]
        result = self.analyzer.analyze(results, "python")
        self.assertTrue(len(result.keywords) > 0)

    def test_sentiment_analysis(self):
        positive_results = [
            SearchResult(
                title="Great innovative breakthrough",
                url="https://example.com",
                snippet="Excellent success with amazing improvements",
                source="test",
            ),
        ]
        result = self.analyzer.analyze(positive_results, "innovation")
        self.assertGreater(result.sentiment_score, 0)

    def test_source_distribution(self):
        results = [
            SearchResult(title="A", url="https://a.com", snippet="s", source="src1"),
            SearchResult(title="B", url="https://b.com", snippet="s", source="src1"),
            SearchResult(title="C", url="https://c.com", snippet="s", source="src2"),
        ]
        result = self.analyzer.analyze(results, "test")
        self.assertEqual(result.source_distribution, {"src1": 2, "src2": 1})

    def test_quality_score(self):
        results = [
            SearchResult(
                title="A very descriptive title with details",
                url="https://example.com",
                snippet="A detailed snippet providing useful information about the topic",
                source="test",
                author="John Doe",
                tags=["tech"],
            ),
        ]
        result = self.analyzer.analyze(results, "test")
        self.assertGreater(result.quality_score, 0)


class TestReportGenerator(unittest.TestCase):
    """Test ReportGenerator."""

    def setUp(self):
        self.gen = ReportGenerator()

    def test_build_report(self):
        results = [
            SearchResult(
                title="Test Result",
                url="https://example.com",
                snippet="Test snippet content",
                source="test_source",
                relevance_score=0.8,
            ),
        ]
        analysis = ContentAnalyzer().analyze(results, "test query")
        report = self.gen.build_report(
            query="test query",
            depth="standard",
            results=results,
            analysis=analysis,
            sources_used=["test_source"],
        )
        self.assertIsNotNone(report.id)
        self.assertEqual(report.query, "test query")
        self.assertEqual(report.total_results, 1)
        self.assertTrue(len(report.references) > 0)

    def test_markdown_generation(self):
        report = ResearchReport(
            id="test123",
            query="test query",
            depth="standard",
            sources_used=["test"],
            total_results=1,
            summary="Test summary",
            conclusion="Test conclusion",
            findings=[{"id": 1, "content": "Finding 1", "type": "finding"}],
            references=[{
                "id": 1,
                "title": "Ref 1",
                "url": "https://example.com",
                "source": "test",
                "relevance": 0.8,
            }],
        )
        md = self.gen.generate(report, "markdown")
        self.assertIn("# 🔬 DeepProbe Research Report", md)
        self.assertIn("test query", md)
        self.assertIn("References", md)

    def test_html_generation(self):
        report = ResearchReport(
            id="test123",
            query="test",
            summary="Test",
            conclusion="Test conclusion",
        )
        html = self.gen.generate(report, "html")
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("<h1>", html)

    def test_json_generation(self):
        report = ResearchReport(
            id="test123",
            query="test",
            summary="Test summary",
        )
        json_str = self.gen.generate(report, "json")
        data = json.loads(json_str)
        self.assertEqual(data["id"], "test123")
        self.assertEqual(data["query"], "test")

    def test_unsupported_format(self):
        with self.assertRaises(ValueError):
            self.gen.generate(ResearchReport(), "xml")


class TestConfigManager(unittest.TestCase):
    """Test ConfigManager."""

    def setUp(self):
        self.config_path = "/tmp/test_deepprobe_config.json"
        self.cm = ConfigManager(self.config_path)

    def tearDown(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    def test_default_config(self):
        self.assertIsNotNone(self.cm.get("search"))
        self.assertEqual(self.cm.get("search.max_results_per_source"), 10)

    def test_get_set(self):
        self.cm.set("search.max_results", 20)
        self.assertEqual(self.cm.get("search.max_results"), 20)

    def test_set_boolean(self):
        self.cm.set("search.cache_enabled", "true")
        self.assertTrue(self.cm.get("search.cache_enabled"))

    def test_set_numeric_string(self):
        self.cm.set("search.request_timeout", "60")
        self.assertEqual(self.cm.get("search.request_timeout"), 60)

    def test_reset(self):
        self.cm.set("search.max_results_per_source", 99)
        self.cm.reset()
        self.assertEqual(self.cm.get("search.max_results_per_source"), 10)

    def test_nonexistent_key(self):
        self.assertIsNone(self.cm.get("nonexistent.key"))
        self.assertEqual(self.cm.get("nonexistent.key", "default"), "default")


class TestStorageEngine(unittest.TestCase):
    """Test StorageEngine."""

    def setUp(self):
        self.db_path = "/tmp/test_deepprobe.db"
        self.storage = StorageEngine(self.db_path)

    def tearDown(self):
        self.storage.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_save_and_get_research(self):
        self.storage.save_research(
            research_id="abc123",
            query="test query",
            depth="standard",
            sources=["duckduckgo"],
            total_results=5,
            analysis={"quality_score": 0.8},
        )
        result = self.storage.get_research("abc123")
        self.assertIsNotNone(result)
        self.assertEqual(result["query"], "test query")
        self.assertEqual(result["total_results"], 5)

    def test_get_nonexistent_research(self):
        result = self.storage.get_research("nonexistent")
        self.assertIsNone(result)

    def test_history(self):
        for i in range(3):
            self.storage.save_research(
                research_id=f"id{i}",
                query=f"query {i}",
                depth="standard",
                sources=["test"],
                total_results=i,
                analysis={},
            )
        history = self.storage.get_history(limit=2)
        self.assertEqual(len(history), 2)

    def test_cache(self):
        self.storage.cache_results(
            query="test",
            source="duckduckgo",
            results=[
                {"title": "Cached", "url": "https://cached.com", "snippet": "s", "relevance_score": 0.5},
            ],
        )
        cached = self.storage.get_cached_results("test", "duckduckgo")
        self.assertEqual(len(cached), 1)
        self.assertEqual(cached[0]["title"], "Cached")

    def test_delete_research(self):
        self.storage.save_research(
            research_id="del_me",
            query="delete test",
            depth="quick",
            sources=["test"],
            total_results=1,
            analysis={},
        )
        result = self.storage.delete_research("del_me")
        # delete_research may return False if no exports were deleted but research was
        self.assertIsNone(self.storage.get_research("del_me"))


class TestSourceRegistry(unittest.TestCase):
    """Test SourceRegistry."""

    def test_register_and_get(self):
        registry = SourceRegistry()
        mock_source = MagicMock(spec=BaseSearchSource)
        mock_source.name = "mock"
        registry.register(mock_source)
        self.assertIsNotNone(registry.get("mock"))
        self.assertIsNone(registry.get("nonexistent"))

    def test_auto_register(self):
        registry = SourceRegistry()
        registry.auto_register()
        all_sources = registry.get_all()
        self.assertGreater(len(all_sources), 0)


if __name__ == "__main__":
    unittest.main()
