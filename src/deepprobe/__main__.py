"""
DeepProbe - Lightweight Local AI Deep Research Engine
轻量级本地AI深度研究引擎

Privacy-first research tool with multi-source search aggregation,
local knowledge graph, and automated report generation.
"""

import argparse
import sys
import os

# Add src to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from deepprobe import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="deepprobe",
        description="🔬 DeepProbe - Lightweight Local AI Deep Research Engine\n"
                    "轻量级本地AI深度研究引擎",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  deepprobe research "artificial intelligence trends 2026"
  deepprobe research "quantum computing applications" --depth deep --format pdf
  deepprobe research "renewable energy" --sources duckduckgo,wikipedia,github
  deepprobe history
  deepprobe export my-research --format markdown
  deepprobe tui
  deepprobe config --set llm.provider openai --set llm.model gpt-4
        """,
    )

    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Research command
    research_parser = subparsers.add_parser(
        "research", help="Start a new deep research task / 启动新的深度研究任务"
    )
    research_parser.add_argument("query", help="Research query / 研究查询关键词")
    research_parser.add_argument(
        "--depth", "-d",
        choices=["quick", "standard", "deep"],
        default="standard",
        help="Research depth: quick/standard/deep / 研究深度 (default: standard)"
    )
    research_parser.add_argument(
        "--sources", "-s",
        default="duckduckgo,wikipedia",
        help="Comma-separated search sources / 搜索源 (default: duckduckgo,wikipedia)"
    )
    research_parser.add_argument(
        "--format", "-f",
        choices=["markdown", "html", "json"],
        default="markdown",
        help="Output format / 输出格式 (default: markdown)"
    )
    research_parser.add_argument(
        "--output", "-o",
        help="Output file path / 输出文件路径"
    )
    research_parser.add_argument(
        "--max-results", "-m",
        type=int,
        default=10,
        help="Max results per source / 每个源最大结果数 (default: 10)"
    )
    research_parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching / 禁用缓存"
    )
    research_parser.add_argument(
        "--language", "-l",
        default="auto",
        help="Report language: auto/zh/en / 报告语言 (default: auto)"
    )

    # History command
    history_parser = subparsers.add_parser(
        "history", help="View research history / 查看研究历史"
    )
    history_parser.add_argument(
        "--limit", "-n",
        type=int,
        default=10,
        help="Number of records to show / 显示记录数 (default: 10)"
    )
    history_parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format / 输出格式"
    )

    # Export command
    export_parser = subparsers.add_parser(
        "export", help="Export a research result / 导出研究结果"
    )
    export_parser.add_argument("id", help="Research ID or keyword / 研究ID或关键词")
    export_parser.add_argument(
        "--format", "-f",
        choices=["markdown", "html", "json"],
        default="markdown",
        help="Export format / 导出格式"
    )
    export_parser.add_argument(
        "--output", "-o",
        help="Output file path / 输出文件路径"
    )

    # TUI command
    subparsers.add_parser(
        "tui", help="Launch terminal UI / 启动终端交互界面"
    )

    # Config command
    config_parser = subparsers.add_parser(
        "config", help="Manage configuration / 管理配置"
    )
    config_parser.add_argument(
        "--set",
        nargs=2,
        action="append",
        metavar=("KEY", "VALUE"),
        help="Set config value (e.g., --set llm.provider openai) / 设置配置项"
    )
    config_parser.add_argument(
        "--get",
        metavar="KEY",
        help="Get config value / 获取配置项"
    )
    config_parser.add_argument(
        "--list",
        action="store_true",
        help="List all config / 列出所有配置"
    )
    config_parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset to defaults / 重置为默认配置"
    )

    # Sources command
    subparsers.add_parser(
        "sources", help="List available search sources / 列出可用搜索源"
    )

    return parser


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "research":
        from deepprobe.core.engine import ResearchEngine
        engine = ResearchEngine()
        result = engine.research(
            query=args.query,
            depth=args.depth,
            sources=args.sources.split(","),
            output_format=args.format,
            output_path=args.output,
            max_results=args.max_results,
            use_cache=not args.no_cache,
            language=args.language,
        )
        if result:
            print(f"\n✅ Research complete! / 研究完成！")
            if args.output:
                print(f"📄 Saved to: {args.output}")
            else:
                print(f"📄 Result saved to local database.")

    elif args.command == "history":
        from deepprobe.core.engine import ResearchEngine
        engine = ResearchEngine()
        engine.show_history(limit=args.limit, fmt=args.format)

    elif args.command == "export":
        from deepprobe.core.engine import ResearchEngine
        engine = ResearchEngine()
        engine.export_result(
            research_id=args.id,
            fmt=args.format,
            output_path=args.output,
        )

    elif args.command == "tui":
        from deepprobe.ui.tui import launch_tui
        launch_tui()

    elif args.command == "config":
        from deepprobe.core.config import ConfigManager
        cm = ConfigManager()
        if args.reset:
            cm.reset()
            print("✅ Configuration reset to defaults. / 配置已重置为默认值。")
        elif args.list:
            cm.list_all()
        elif args.get:
            value = cm.get(args.get)
            print(f"{args.get} = {value}")
        elif args.set:
            for key, value in args.set:
                cm.set(key, value)
                print(f"✅ Set {key} = {value}")
        else:
            cm.list_all()

    elif args.command == "sources":
        from deepprobe.search.registry import SourceRegistry
        registry = SourceRegistry()
        registry.auto_register()
        registry.list_sources()


if __name__ == "__main__":
    main()
