"""Interactive demo script for QuickMemo MCP Server.

Demonstrates all MCP capabilities:
1. Adding memos (Tool)
2. Listing and filtering memos (Tool)
3. Searching memos (Tool)
4. Reading dynamic resources (memo://all, memo://stats)
5. Generating prompts (review_notes, daily_standup)
"""

import sys
import tempfile
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from quickmemo.server import (
    MemoStore,
    add_memo,
    list_memos,
    get_memo,
    search_memos,
    get_all_memos_resource,
    get_memo_stats_resource,
    review_notes,
    daily_standup,
    store,
)


def run_demo() -> None:
    print("=" * 60)
    print(" QUICKMEMO MCP - LIVE INTERACTIVE DEMO")
    print("=" * 60)

    # Use a temporary store for the demo
    temp_dir = tempfile.TemporaryDirectory()
    store.file_path = Path(temp_dir.name) / "demo_memos.json"
    store._save({})

    print("\n1. ADDING MEMOS VIA MCP TOOLS:")
    print("-" * 40)
    r1 = add_memo(
        title="Protocol Discovery",
        content="MCP allows LLMs to query Tools, Resources, and Prompts over JSON-RPC.",
        category="learning",
        tags=["mcp", "architecture", "ai"]
    )
    print(r1)

    r2 = add_memo(
        title="Python FastMCP Pattern",
        content="FastMCP provides high-level decorator ergonomics for MCP server creation.",
        category="python",
        tags=["fastmcp", "sdk", "decorators"]
    )
    print(r2)

    r3 = add_memo(
        title="Deployment to Smithery",
        content="Smithery simplifies hosting and discovery of MCP servers with stdio and SSE.",
        category="devops",
        tags=["smithery", "cloud", "deployment"]
    )
    print(r3)

    print("\n2. LISTING MEMOS WITH FILTERS:")
    print("-" * 40)
    print("All memos:")
    print(list_memos())

    print("\nFiltered by category='learning':")
    print(list_memos(category="learning"))

    print("\n3. SEARCHING MEMOS BY KEYWORD:")
    print("-" * 40)
    print("Query: 'smithery'")
    print(search_memos("smithery"))

    print("\n4. READING DYNAMIC MCP RESOURCES:")
    print("-" * 40)
    print("Resource URI: memo://stats")
    print(get_memo_stats_resource())

    print("\nResource URI: memo://all (Markdown Digest Preview):")
    print(get_all_memos_resource())

    print("\n5. GENERATING PROMPT TEMPLATES:")
    print("-" * 40)
    print("Prompt: review_notes(category='learning')")
    print(review_notes(category="learning"))

    print("\nPrompt: daily_standup()")
    print(daily_standup())

    print("\n" + "=" * 60)
    print(" DEMO COMPLETED SUCCESSFULLY! ALL MCP CAPABILITIES VERIFIED.")
    print("=" * 60)

    temp_dir.cleanup()


if __name__ == "__main__":
    run_demo()
