"""
Terminal User Interface (TUI) for DeepProbe.
DeepProbe终端交互界面。
"""

import os
import sys
import signal
from typing import Optional, List


# ANSI color codes
class Colors:
    """Terminal color codes."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BG_BLUE = "\033[44m"
    BG_DARK = "\033[48;5;236m"


def color_enabled() -> bool:
    """Check if terminal supports colors."""
    if os.environ.get("NO_COLOR"):
        return False
    if not sys.stdout.isatty():
        return False
    return True


def c(text: str, color: str) -> str:
    """Apply color to text if supported."""
    if color_enabled():
        return f"{color}{text}{Colors.RESET}"
    return text


def print_banner():
    """Print the DeepProbe banner."""
    banner = f"""
{c('╔══════════════════════════════════════════════════════════╗', Colors.CYAN)}
{c('║', Colors.CYAN)}                                                          {c('║', Colors.CYAN)}
{c('║', Colors.CYAN)}  {c('███████╗ ██████╗ ███╗   ██╗ ██████╗ ██████╗ ███████╗', Colors.GREEN)}  {c('║', Colors.CYAN)}
{c('║', Colors.CYAN)}  {c('██╔════╝██╔═══██╗████╗  ██║██╔════╝ ██╔══██╗██╔════╝', Colors.GREEN)}  {c('║', Colors.CYAN)}
{c('║', Colors.CYAN)}  {c('█████╗  ██║   ██║██╔██╗ ██║██║  ███╗██████╔╝█████╗  ', Colors.GREEN)}  {c('║', Colors.CYAN)}
{c('║', Colors.CYAN)}  {c('██╔══╝  ██║   ██║██║╚██╗██║██║   ██║██╔══██╗██╔══╝  ', Colors.GREEN)}  {c('║', Colors.CYAN)}
{c('║', Colors.CYAN)}  {c('██║     ╚██████╔╝██║ ╚████║╚██████╔╝██║  ██║███████╗', Colors.GREEN)}  {c('║', Colors.CYAN)}
{c('║', Colors.CYAN)}  {c('╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝', Colors.GREEN)}  {c('║', Colors.CYAN)}
{c('║', Colors.CYAN)}                                                          {c('║', Colors.CYAN)}
{c('║', Colors.CYAN)}  {c('🔬 Lightweight Local AI Deep Research Engine', Colors.BOLD)}          {c('║', Colors.CYAN)}
{c('║', Colors.CYAN)}  {c('   轻量级本地AI深度研究引擎', Colors.DIM)}                            {c('║', Colors.CYAN)}
{c('║', Colors.CYAN)}                                                          {c('║', Colors.CYAN)}
{c('╚══════════════════════════════════════════════════════════╝', Colors.CYAN)}
"""
    print(banner)


def print_menu():
    """Print the main menu."""
    print(f"\n{c('  ┌─ Main Menu ─────────────────────────────┐', Colors.CYAN)}")
    print(f"{c('  │', Colors.CYAN)}                                          {c('│', Colors.CYAN)}")
    print(f"  {c('│', Colors.CYAN)}  {c('1.', Colors.YELLOW)}  🔍 New Research / 新建研究        {c('│', Colors.CYAN)}")
    print(f"  {c('│', Colors.CYAN)}  {c('2.', Colors.YELLOW)}  📚 History / 历史记录             {c('│', Colors.CYAN)}")
    print(f"  {c('│', Colors.CYAN)}  {c('3.', Colors.YELLOW)}  📤 Export / 导出报告              {c('│', Colors.CYAN)}")
    print(f"  {c('│', Colors.CYAN)}  {c('4.', Colors.YELLOW)}  🔎 Sources / 搜索源管理           {c('│', Colors.CYAN)}")
    print(f"  {c('│', Colors.CYAN)}  {c('5.', Colors.YELLOW)}  ⚙️  Config / 配置管理             {c('│', Colors.CYAN)}")
    print(f"  {c('│', Colors.CYAN)}  {c('0.', Colors.RED)}  Exit / 退出                     {c('│', Colors.CYAN)}")
    print(f"{c('  └──────────────────────────────────────────┘', Colors.CYAN)}")


def prompt(text: str, default: str = "") -> str:
    """Prompt for user input."""
    suffix = f" ({c(default, Colors.DIM)})" if default else ""
    try:
        value = input(f"\n  {c('❯', Colors.GREEN)} {text}{suffix}: ").strip()
        return value or default
    except (EOFError, KeyboardInterrupt):
        print()
        return ""


def prompt_choice(text: str, choices: List[str], default: str = "") -> str:
    """Prompt for a choice from a list."""
    print(f"\n  {text}")
    for i, choice in enumerate(choices, 1):
        marker = f" {c('(default)', Colors.DIM)}" if choice == default else ""
        print(f"    {c(f'{i}.', Colors.YELLOW)} {choice}{marker}")

    while True:
        value = prompt("Select", default or "1")
        if value.isdigit() and 1 <= int(value) <= len(choices):
            return choices[int(value) - 1]
        if value.lower() in [c.lower() for c in choices]:
            return choices[[c.lower() for c in choices].index(value.lower())]
        print(f"  {c('⚠️ Invalid choice, try again.', Colors.YELLOW)}")


def launch_tui():
    """Launch the terminal UI."""
    print_banner()

    # Import here to avoid circular imports
    from ..core.engine import ResearchEngine
    from ..search.registry import SourceRegistry

    engine = ResearchEngine()

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print(f"\n\n  {c('👋 Goodbye! / 再见！', Colors.CYAN)}\n")
        engine.cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    while True:
        print_menu()
        choice = prompt("Enter choice", "1")

        if choice == "0" or choice.lower() in ("q", "quit", "exit"):
            print(f"\n  {c('👋 Goodbye! / 再见！', Colors.CYAN)}\n")
            engine.cleanup()
            break

        elif choice == "1":
            # New Research
            query = prompt("Research query / 研究关键词")
            if not query:
                print(f"  {c('⚠️ Query cannot be empty.', Colors.YELLOW)}")
                continue

            depth = prompt_choice(
                "Research depth / 研究深度:",
                ["quick", "standard", "deep"],
                default="standard",
            )

            sources = prompt(
                "Sources (comma-separated, e.g., duckduckgo,wikipedia,github,arxiv,news) / 搜索源",
                default="duckduckgo,wikipedia",
            )

            fmt = prompt_choice(
                "Output format / 输出格式:",
                ["markdown", "html", "json"],
                default="markdown",
            )

            output = prompt("Output file path (optional) / 输出路径（可选）", default="")

            print()
            engine.research(
                query=query,
                depth=depth,
                sources=[s.strip() for s in sources.split(",") if s.strip()],
                output_format=fmt,
                output_path=output or None,
            )

        elif choice == "2":
            # History
            limit = prompt("Number of records / 记录数", "10")
            try:
                engine.show_history(limit=int(limit))
            except ValueError:
                engine.show_history()

        elif choice == "3":
            # Export
            research_id = prompt("Research ID or keyword / 研究ID或关键词")
            if not research_id:
                continue

            fmt = prompt_choice(
                "Export format / 导出格式:",
                ["markdown", "html", "json"],
                default="markdown",
            )

            output = prompt("Output file path (optional) / 输出路径（可选）", default="")
            engine.export_result(research_id, fmt=fmt, output_path=output or None)

        elif choice == "4":
            # Sources
            registry = SourceRegistry()
            registry.auto_register()
            registry.list_sources()

        elif choice == "5":
            # Config
            from ..core.config import ConfigManager
            cm = ConfigManager()
            action = prompt_choice(
                "Config action / 配置操作:",
                ["list", "set", "reset"],
                default="list",
            )

            if action == "list":
                cm.list_all()
            elif action == "set":
                key = prompt("Config key (e.g., search.default_sources) / 配置键")
                value = prompt("Config value / 配置值")
                if key and value:
                    cm.set(key, value)
                    print(f"  {c(f'✅ Set {key} = {value}', Colors.GREEN)}")
            elif action == "reset":
                cm.reset()
                print(f"  {c('✅ Configuration reset.', Colors.GREEN)}")

        else:
            print(f"  {c('⚠️ Invalid choice.', Colors.YELLOW)}")
