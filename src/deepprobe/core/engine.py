"""
Core research engine - orchestrates the full research pipeline.
核心研究引擎 - 编排完整研究流程。
"""

import hashlib
import os
import sys
import time
from datetime import datetime
from typing import List, Optional

from .config import ConfigManager
from ..search.registry import SourceRegistry, SearchResult
from ..analysis.content_analyzer import ContentAnalyzer, AnalysisResult
from ..report.generator import ReportGenerator, ResearchReport
from ..storage.engine import StorageEngine


class ProgressCallback:
    """Simple progress callback for research pipeline."""

    def __init__(self, enabled: bool = True):
        self._enabled = enabled
        self._steps = 0
        self._total = 0

    def start(self, total_steps: int, message: str = ""):
        """Start progress tracking."""
        self._total = total_steps
        self._steps = 0
        if self._enabled:
            print(f"\n{'='*60}")
            print(f"🔬 DeepProbe Research Engine")
            print(f"{'='*60}")
            if message:
                print(f"📋 {message}")

    def step(self, message: str):
        """Record a progress step."""
        self._steps += 1
        if self._enabled:
            pct = int((self._steps / max(self._total, 1)) * 100)
            bar_len = 30
            filled = int(bar_len * pct / 100)
            bar = "█" * filled + "░" * (bar_len - filled)
            print(f"\r  [{bar}] {pct}% | {message}", end="", flush=True)

    def complete(self, message: str = ""):
        """Mark progress as complete."""
        if self._enabled:
            print(f"\r  [{'█'*30}] 100% | ✅ {message}")
            print(f"{'='*60}\n")


class ResearchEngine:
    """Main research engine that orchestrates the full pipeline."""

    DEPTH_CONFIG = {
        "quick": {"max_results": 5, "sources": ["duckduckgo"]},
        "standard": {"max_results": 10, "sources": ["duckduckgo", "wikipedia"]},
        "deep": {"max_results": 20, "sources": ["duckduckgo", "wikipedia", "github", "arxiv", "news"]},
    }

    def __init__(self, config_path: Optional[str] = None):
        self._config = ConfigManager(config_path)
        self._registry = SourceRegistry()
        self._registry.auto_register()
        self._analyzer = ContentAnalyzer()
        self._report_gen = ReportGenerator()
        self._storage = StorageEngine(
            self._config.get("storage.database_path")
        )
        self._progress = ProgressCallback(
            self._config.get("ui.progress_enabled", True)
        )

    def research(
        self,
        query: str,
        depth: str = "standard",
        sources: Optional[List[str]] = None,
        output_format: str = "markdown",
        output_path: Optional[str] = None,
        max_results: int = 10,
        use_cache: bool = True,
        language: str = "auto",
    ) -> Optional[ResearchReport]:
        """Execute a full research pipeline.

        Args:
            query: Research query.
            depth: Research depth (quick/standard/deep).
            sources: List of search source names.
            output_format: Output format (markdown/html/json).
            output_path: Optional output file path.
            max_results: Max results per source.
            use_cache: Whether to use cached results.
            language: Report language.

        Returns:
            ResearchReport if successful, None otherwise.
        """
        start_time = time.time()

        # Determine depth config
        depth_cfg = self.DEPTH_CONFIG.get(depth, self.DEPTH_CONFIG["standard"])
        if not sources:
            sources = depth_cfg["sources"]
        effective_max = min(max_results, depth_cfg["max_results"] * 2)

        total_steps = len(sources) + 3  # search + analyze + report + save
        self._progress.start(total_steps, f'Query: "{query}" | Depth: {depth}')

        # Step 1: Search
        all_results: List[SearchResult] = []
        active_sources = []

        for source_name in sources:
            source = self._registry.get(source_name)
            if not source:
                self._progress.step(f"⚠️ Source '{source_name}' not found, skipping")
                continue

            if not source.is_available():
                self._progress.step(f"⚠️ Source '{source_name}' unavailable, skipping")
                continue

            self._progress.step(f"🔍 Searching {source_name}...")

            # Check cache first
            if use_cache:
                cached = self._storage.get_cached_results(query, source_name)
                if cached:
                    for c in cached:
                        all_results.append(SearchResult(**c))
                    self._progress.step(f"📦 {source_name}: {len(cached)} cached results")
                    active_sources.append(source_name)
                    continue

            try:
                results = source.search(query, max_results=effective_max)
                all_results.extend(results)
                active_sources.append(source_name)

                # Cache results
                if use_cache and results:
                    self._storage.cache_results(
                        query, source_name,
                        [r.to_dict() for r in results],
                        ttl_hours=self._config.get("search.cache_ttl_hours", 24),
                    )

                self._progress.step(f"✅ {source_name}: {len(results)} results")
            except Exception as e:
                self._progress.step(f"❌ {source_name}: {str(e)[:50]}")

        if not all_results:
            self._progress.step("⚠️ No results found!")
            return None

        # Deduplicate by URL
        seen_urls = set()
        unique_results = []
        for r in all_results:
            if r.url not in seen_urls:
                seen_urls.add(r.url)
                unique_results.append(r)
        all_results = unique_results

        # Step 2: Analyze
        self._progress.step("📊 Analyzing content...")
        analysis = self._analyzer.analyze(all_results, query)

        # Step 3: Generate Report
        self._progress.step("📝 Generating report...")
        report = self._report_gen.build_report(
            query=query,
            depth=depth,
            results=all_results,
            analysis=analysis,
            sources_used=active_sources,
        )

        # Step 4: Save to storage
        self._progress.step("💾 Saving to local database...")
        self._storage.save_research(
            research_id=report.id,
            query=query,
            depth=depth,
            sources=active_sources,
            total_results=len(all_results),
            analysis=report.analysis or {},
        )

        # Step 5: Export
        if output_path:
            self._progress.step(f"📄 Exporting to {output_path}...")
            self._report_gen.generate(report, output_format, output_path)
        else:
            # Auto-save to exports directory
            export_dir = os.path.expanduser(
                self._config.get("storage.export_dir", "~/.deepprobe/exports")
            )
            os.makedirs(export_dir, exist_ok=True)
            auto_path = os.path.join(
                export_dir,
                f"{report.id}_{query[:30].replace(' ', '_')}.{output_format}",
            )
            self._report_gen.generate(report, output_format, auto_path)

        elapsed = time.time() - start_time
        self._progress.complete(
            f"Done in {elapsed:.1f}s | {len(all_results)} results from {len(active_sources)} sources"
        )

        # Print brief summary
        print(f"📋 Report ID: {report.id}")
        print(f"📊 Quality: {analysis.quality_score:.1%} | "
              f"Coverage: {analysis.coverage_score:.1%} | "
              f"Sentiment: {analysis.sentiment_score:+.2f}")
        if analysis.keywords:
            top_kw = ", ".join(kw for kw, _ in analysis.keywords[:5])
            print(f"🔑 Top Keywords: {top_kw}")

        return report

    def show_history(self, limit: int = 10, fmt: str = "table") -> None:
        """Display research history."""
        history = self._storage.get_history(limit)

        if not history:
            print("📭 No research history found. / 暂无研究历史。")
            return

        if fmt == "json":
            import json
            print(json.dumps(history, indent=2, ensure_ascii=False))
            return

        print(f"\n📚 Research History (last {limit})")
        print("=" * 80)
        print(f"  {'ID':<14} {'Query':<30} {'Depth':<10} {'Results':<8} {'Date'}")
        print("-" * 80)

        for item in history:
            query = item["query"][:28] + ".." if len(item["query"]) > 28 else item["query"]
            date = item["created_at"][:10]
            status_icon = "✅" if item["status"] == "completed" else "⏳"
            print(f"  {status_icon} {item['id']:<12} {query:<30} {item['depth']:<10} "
                  f"{item['total_results']:<8} {date}")

        print("=" * 80)

    def export_result(
        self,
        research_id: str,
        fmt: str = "markdown",
        output_path: Optional[str] = None,
    ) -> None:
        """Export a research result."""
        # Try to find by ID first, then by keyword
        data = self._storage.get_research(research_id)
        if not data:
            results = self._storage.search_research(research_id, limit=1)
            if results:
                data = results[0]

        if not data:
            print(f"❌ Research '{research_id}' not found.")
            return

        # Reconstruct report from stored data
        report = ResearchReport(
            id=data["id"],
            query=data["query"],
            depth=data["depth"],
            created_at=data["created_at"],
            sources_used=data["sources"],
            total_results=data["total_results"],
            analysis=data.get("analysis", {}),
            summary=data.get("analysis", {}).get("summary", ""),
        )

        content = self._report_gen.generate(report, fmt, output_path)

        if not output_path:
            export_dir = os.path.expanduser("~/.deepprobe/exports")
            os.makedirs(export_dir, exist_ok=True)
            output_path = os.path.join(
                export_dir,
                f"{report.id}_export.{fmt}",
            )
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

        print(f"✅ Exported to: {output_path}")

    def cleanup(self) -> None:
        """Clean up resources."""
        cleared = self._storage.clear_expired_cache()
        if cleared > 0:
            print(f"🧹 Cleared {cleared} expired cache entries.")
        self._storage.close()
