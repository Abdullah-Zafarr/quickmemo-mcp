"""Interactive Client Demo & Verification Script for VaultCraft MCP Server.

Connects to the VaultCraft MCP Server, exercises tools, queries resources,
and renders prompt templates.
"""

import sys
from pathlib import Path

# Configure utf-8 stdout for Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vaultcraft.server import (
    create_or_update_note,
    read_note,
    search_vault,
    find_backlinks,
    get_graph_metrics,
    log_daily_entry,
    get_note_resource,
    get_today_daily_resource,
    get_graph_overview_resource,
    synthesize_concept,
    daily_standup,
    knowledge_gap_analysis,
)


def print_section(title: str):
    print("\n" + "=" * 70)
    print(f"  🚀 {title.upper()}")
    print("=" * 70)


def run_demo():
    print_section("1. Creating Atomic Zettelkasten Notes (MCP Tools)")
    
    r1 = create_or_update_note(
        title="Model Context Protocol",
        content="MCP is an open standard that enables AI models to interact with [[Tools]], [[Resources]], and [[Prompts]]. See [[FastMCP Architecture]] for implementation.",
        tags=["mcp", "architecture", "ai"]
    )
    print(r1)

    r2 = create_or_update_note(
        title="FastMCP Architecture",
        content="FastMCP provides a clean Pythonic decorator interface for creating [[Model Context Protocol]] servers with zero boilerplate.",
        tags=["mcp", "python", "fastmcp"]
    )
    print(r2)

    r3 = create_or_update_note(
        title="Knowledge Graph Theory",
        content="Knowledge graphs represent entities as nodes and relationships as edges. [[Model Context Protocol]] servers can expose graphs to LLMs.",
        tags=["graph", "knowledge-management"]
    )
    print(r3)

    r4 = create_or_update_note(
        title="Orphan Idea",
        content="A note with no links to anywhere yet.",
        tags=["misc"]
    )
    print(r4)

    print_section("2. Searching the Vault (MCP Tool: search_vault)")
    search_results = search_vault(query="FastMCP")
    print(search_results)

    print_section("3. Finding Bidirectional Backlinks (MCP Tool: find_backlinks)")
    backlinks = find_backlinks("Model Context Protocol")
    print(backlinks)

    print_section("4. Knowledge Graph Health & Metrics (MCP Tool: get_graph_metrics)")
    metrics = get_graph_metrics()
    print(metrics)

    print_section("5. Logging Daily Developer Activity (MCP Tool: log_daily_entry)")
    log_res = log_daily_entry("Built VaultCraft MCP server with tools, resources, and prompts.", category="Milestone")
    print(log_res)
    log_res2 = log_daily_entry("Passed all 10 unit and functional tests with pytest.", category="Testing")
    print(log_res2)

    print_section("6. Accessing Direct Dynamic Resources (MCP Resource)")
    print("--- [vault://notes/Model Context Protocol] ---")
    print(get_note_resource("Model Context Protocol"))
    print("\n--- [vault://daily/today] ---")
    print(get_today_daily_resource())

    print_section("7. Generating Dynamic MCP Prompts (MCP Prompt)")
    print("--- [synthesize_concept(tag='mcp')] ---")
    synth = synthesize_concept(tag="mcp", objective="Summarize MCP building concepts")
    print(synth[:400] + "...\n[Truncated for display]")

    print("--- [daily_standup()] ---")
    standup = daily_standup()
    print(standup)

    print_section("VaultCraft MCP Demo Finished Successfully ✅")


if __name__ == "__main__":
    run_demo()
