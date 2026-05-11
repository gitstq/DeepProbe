"""
Report generator - creates research reports in multiple formats.
报告生成器 - 支持多格式研究报告生成。
"""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional

from ..search.registry import SearchResult, SourceType
from ..analysis.content_analyzer import AnalysisResult


@dataclass
class ResearchReport:
    """Complete research report data structure."""
    id: str = ""
    query: str = ""
    depth: str = "standard"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    sources_used: List[str] = field(default_factory=list)
    total_results: int = 0
    analysis: Optional[dict] = None
    findings: List[dict] = field(default_factory=list)
    references: List[dict] = field(default_factory=list)
    summary: str = ""
    conclusion: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


class ReportGenerator:
    """Generates research reports in multiple formats."""

    def __init__(self):
        self._generators = {
            "markdown": self._generate_markdown,
            "html": self._generate_html,
            "json": self._generate_json,
        }

    def generate(
        self,
        report: ResearchReport,
        fmt: str = "markdown",
        output_path: Optional[str] = None,
    ) -> str:
        """Generate a report in the specified format.

        Args:
            report: ResearchReport data.
            fmt: Output format (markdown/html/json).
            output_path: Optional file path to save the report.

        Returns:
            Generated report content as string.
        """
        generator = self._generators.get(fmt)
        if not generator:
            raise ValueError(f"Unsupported format: {fmt}. Supported: {list(self._generators.keys())}")

        content = generator(report)

        if output_path:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

        return content

    def build_report(
        self,
        query: str,
        depth: str,
        results: List[SearchResult],
        analysis: AnalysisResult,
        sources_used: List[str],
    ) -> ResearchReport:
        """Build a ResearchReport from search results and analysis."""
        import hashlib

        report_id = hashlib.md5(
            f"{query}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        # Build findings from analysis
        findings = []
        for i, finding in enumerate(analysis.key_findings, 1):
            findings.append({
                "id": i,
                "content": finding,
                "type": "finding",
            })

        # Build references
        references = []
        for i, result in enumerate(results, 1):
            references.append({
                "id": i,
                "title": result.title,
                "url": result.url,
                "source": result.source,
                "snippet": result.snippet[:200],
                "relevance": round(result.relevance_score, 3),
            })

        # Generate conclusion
        conclusion = self._generate_conclusion(analysis, query)

        return ResearchReport(
            id=report_id,
            query=query,
            depth=depth,
            sources_used=sources_used,
            total_results=len(results),
            analysis={
                "keywords": analysis.keywords[:10],
                "themes": analysis.themes,
                "sentiment_score": round(analysis.sentiment_score, 3),
                "quality_score": round(analysis.quality_score, 3),
                "coverage_score": round(analysis.coverage_score, 3),
                "source_distribution": analysis.source_distribution,
                "entity_mentions": analysis.entity_mentions,
            },
            findings=findings,
            references=references,
            summary=analysis.summary,
            conclusion=conclusion,
        )

    def _generate_conclusion(self, analysis: AnalysisResult, query: str) -> str:
        """Generate a conclusion based on analysis."""
        top_keywords = [kw for kw, _ in analysis.keywords[:5]]
        keyword_str = ", ".join(top_keywords)

        parts = [
            f"This research on '{query}' analyzed {analysis.source_distribution} "
            f"data sources with an overall quality score of {analysis.quality_score:.1%}.",
        ]

        if keyword_str:
            parts.append(f"The most prominent topics are: {keyword_str}.")

        if analysis.themes:
            themes_str = "; ".join(analysis.themes[:3])
            parts.append(f"Key themes identified: {themes_str}.")

        sentiment_desc = "generally positive" if analysis.sentiment_score > 0.2 else \
                        "mixed" if abs(analysis.sentiment_score) <= 0.2 else \
                        "generally negative"
        parts.append(
            f"The overall sentiment across sources is {sentiment_desc} "
            f"(score: {analysis.sentiment_score:.2f})."
        )

        if analysis.coverage_score < 0.5:
            parts.append(
                "Note: Query coverage is limited. Consider broadening "
                "search terms or adding more sources for comprehensive results."
            )

        return " ".join(parts)

    def _generate_markdown(self, report: ResearchReport) -> str:
        """Generate Markdown format report."""
        lines = []

        # Header
        lines.append(f"# 🔬 DeepProbe Research Report")
        lines.append("")
        lines.append(f"**Query**: {report.query}")
        lines.append(f"**Depth**: {report.depth}")
        lines.append(f"**Date**: {report.created_at[:10]}")
        lines.append(f"**Report ID**: `{report.id}`")
        lines.append(f"**Sources**: {', '.join(report.sources_used)}")
        lines.append(f"**Total Results**: {report.total_results}")
        lines.append("")

        # Summary
        lines.append("---")
        lines.append("")
        lines.append("## 📋 Executive Summary")
        lines.append("")
        lines.append(report.summary)
        lines.append("")

        # Analysis
        if report.analysis:
            lines.append("## 📊 Analysis")
            lines.append("")

            # Keywords
            keywords = report.analysis.get("keywords", [])
            if keywords:
                lines.append("### 🔑 Key Keywords")
                lines.append("")
                lines.append("| Keyword | Relevance Score |")
                lines.append("|---------|----------------|")
                for kw, score in keywords[:10]:
                    bar = "█" * int(score * 20)
                    lines.append(f"| {kw} | {score:.4f} {bar} |")
                lines.append("")

            # Themes
            themes = report.analysis.get("themes", [])
            if themes:
                lines.append("### 🎯 Key Themes")
                lines.append("")
                for theme in themes:
                    lines.append(f"- {theme}")
                lines.append("")

            # Scores
            lines.append("### 📈 Metrics")
            lines.append("")
            lines.append(f"- **Quality Score**: {report.analysis.get('quality_score', 0):.1%}")
            lines.append(f"- **Coverage Score**: {report.analysis.get('coverage_score', 0):.1%}")
            lines.append(f"- **Sentiment**: {report.analysis.get('sentiment_score', 0):.2f}")
            lines.append("")

            # Source Distribution
            source_dist = report.analysis.get("source_distribution", {})
            if source_dist:
                lines.append("### 📡 Source Distribution")
                lines.append("")
                for source, count in source_dist.items():
                    lines.append(f"- **{source}**: {count} results")
                lines.append("")

            # Entity Mentions
            entities = report.analysis.get("entity_mentions", {})
            if entities:
                lines.append("### 🏢 Entity Mentions")
                lines.append("")
                for entity, count in list(entities.items())[:10]:
                    lines.append(f"- **{entity}**: {count} mentions")
                lines.append("")

        # Key Findings
        if report.findings:
            lines.append("## 🔍 Key Findings")
            lines.append("")
            for finding in report.findings:
                lines.append(f"### Finding #{finding['id']}")
                lines.append("")
                lines.append(finding["content"])
                lines.append("")

        # References
        if report.references:
            lines.append("## 📚 References")
            lines.append("")
            for ref in report.references:
                lines.append(f"{ref['id']}. **[{ref['title']}]({ref['url']})**")
                lines.append(f"   - Source: {ref['source']} | Relevance: {ref['relevance']:.2f}")
                if ref.get("snippet"):
                    lines.append(f"   - {ref['snippet']}")
                lines.append("")

        # Conclusion
        lines.append("## 💡 Conclusion")
        lines.append("")
        lines.append(report.conclusion)
        lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*Generated by [DeepProbe](https://github.com/gitstq/DeepProbe) "
                      f"on {report.created_at} | MIT License*")

        return "\n".join(lines)

    def _generate_html(self, report: ResearchReport) -> str:
        """Generate HTML format report."""
        md_content = self._generate_markdown(report)

        # Simple Markdown-to-HTML conversion
        html = md_content
        html = html.replace("&", "&amp;")
        html = html.replace("<", "&lt;").replace(">", "&gt;")

        # Headers
        import re
        html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
        html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)

        # Bold
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)

        # Links
        html = re.sub(
            r"\[(.+?)\]\((.+?)\)",
            r'<a href="\2" target="_blank">\1</a>',
            html,
        )

        # Code
        html = re.sub(r"`(.+?)`", r"<code>\1</code>", html)

        # Lists
        html = re.sub(r"^- (.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)
        html = re.sub(r"(<li>.*</li>\n?)+", r"<ul>\g<0></ul>", html)

        # Tables (simplified)
        html = re.sub(r"^\|.*\|$", lambda m: self._table_row(m.group()), html, flags=re.MULTILINE)

        # Horizontal rules
        html = re.sub(r"^---$", r"<hr>", html, flags=re.MULTILINE)

        # Paragraphs
        html = re.sub(r"\n\n", r"</p><p>", html)
        html = f"<p>{html}</p>"

        # Wrap in document
        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DeepProbe Research: {report.query}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{ color: #1a1a2e; border-bottom: 3px solid #16213e; padding-bottom: 10px; }}
        h2 {{ color: #16213e; border-bottom: 1px solid #ddd; padding-bottom: 5px; margin-top: 30px; }}
        h3 {{ color: #0f3460; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }}
        a {{ color: #0f3460; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
        th {{ background: #16213e; color: white; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        hr {{ border: none; border-top: 2px solid #eee; margin: 30px 0; }}
        li {{ margin: 5px 0; }}
    </style>
</head>
<body>
{html}
</body>
</html>"""

        return full_html

    @staticmethod
    def _table_row(row: str) -> str:
        """Convert a Markdown table row to HTML."""
        if "---" in row:
            return ""
        cells = [c.strip() for c in row.strip("|").split("|")]
        tag = "th" if "Keyword" in row or "Source" in row else "td"
        return "<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>"

    def _generate_json(self, report: ResearchReport) -> str:
        """Generate JSON format report."""
        return json.dumps(report.to_dict(), indent=2, ensure_ascii=False)
