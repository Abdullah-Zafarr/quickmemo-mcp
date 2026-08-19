"""QuickMemo MCP - A minimalistic and elegant context memo engine for Model Context Protocol.

Provides fast, structured micro-note capture, search, dynamic resources, and prompt templates for AI assistants.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import MCPServer
from pydantic import BaseModel, Field

# Storage configuration
DEFAULT_STORAGE_DIR = Path.home() / ".quickmemo"
STORAGE_FILE = Path(os.environ.get("QUICKMEMO_STORAGE", str(DEFAULT_STORAGE_DIR / "memos.json")))


class Memo(BaseModel):
    """Data model representing a quick context memo."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str
    content: str
    category: str = "general"
    tags: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MemoStore:
    """Lightweight persistent storage for memos."""

    def __init__(self, file_path: Path = STORAGE_FILE):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._save({})

    def _load(self) -> Dict[str, Dict[str, Any]]:
        try:
            if self.file_path.exists():
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save(self, data: Dict[str, Dict[str, Any]]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add(self, title: str, content: str, category: str = "general", tags: Optional[List[str]] = None) -> Memo:
        memos = self._load()
        memo = Memo(
            title=title.strip(),
            content=content.strip(),
            category=category.strip().lower() or "general",
            tags=[t.strip().lower() for t in (tags or []) if t.strip()]
        )
        memos[memo.id] = memo.model_dump()
        self._save(memos)
        return memo

    def list_all(self, category: Optional[str] = None, tag: Optional[str] = None) -> List[Memo]:
        memos = [Memo(**data) for data in self._load().values()]
        if category:
            memos = [m for m in memos if m.category.lower() == category.strip().lower()]
        if tag:
            tag_lower = tag.strip().lower()
            memos = [m for m in memos if tag_lower in [t.lower() for t in m.tags]]
        return sorted(memos, key=lambda m: m.created_at, reverse=True)

    def get(self, memo_id: str) -> Optional[Memo]:
        memos = self._load()
        data = memos.get(memo_id)
        return Memo(**data) if data else None

    def search(self, query: str) -> List[Memo]:
        q = query.lower().strip()
        memos = [Memo(**data) for data in self._load().values()]
        results = [
            m for m in memos
            if q in m.title.lower() or q in m.content.lower() or any(q in t.lower() for t in m.tags) or q in m.category.lower()
        ]
        return sorted(results, key=lambda m: m.created_at, reverse=True)

    def delete(self, memo_id: str) -> bool:
        memos = self._load()
        if memo_id in memos:
            del memos[memo_id]
            self._save(memos)
            return True
        return False

    def clear(self) -> int:
        memos = self._load()
        count = len(memos)
        self._save({})
        return count


# Initialize server and store
store = MemoStore()
server = MCPServer(name="quickmemo")


# ============================================================================
# MCP TOOLS
# ============================================================================

@server.tool(
    name="add_memo",
    description="Save a new context memo, snippet, or idea with optional category and tags."
)
def add_memo(
    title: str,
    content: str,
    category: str = "general",
    tags: Optional[List[str]] = None
) -> str:
    """Save a new memo and return the formatted confirmation."""
    memo = store.add(title=title, content=content, category=category, tags=tags or [])
    tag_str = f" [{', '.join(memo.tags)}]" if memo.tags else ""
    return f"Created Memo #{memo.id}: '{memo.title}' in [{memo.category}]{tag_str}\n{memo.content}"


@server.tool(
    name="list_memos",
    description="List saved memos with optional category and tag filtering."
)
def list_memos(
    category: Optional[str] = None,
    tag: Optional[str] = None
) -> str:
    """List all matching memos."""
    memos = store.list_all(category=category, tag=tag)
    if not memos:
        filters = []
        if category:
            filters.append(f"category='{category}'")
        if tag:
            filters.append(f"tag='{tag}'")
        filter_str = f" matching {', '.join(filters)}" if filters else ""
        return f"No memos found{filter_str}."

    lines = [f"Found {len(memos)} memo(s):"]
    for m in memos:
        tag_str = f" ({', '.join(m.tags)})" if m.tags else ""
        preview = m.content.replace("\n", " ")[:60]
        if len(m.content) > 60:
            preview += "..."
        lines.append(f"- [#{m.id}] **{m.title}** [{m.category}]{tag_str} -> {preview}")
    return "\n".join(lines)


@server.tool(
    name="get_memo",
    description="Retrieve the full details and content of a specific memo by ID."
)
def get_memo(memo_id: str) -> str:
    """Get a specific memo."""
    memo = store.get(memo_id.strip())
    if not memo:
        return f"Error: Memo #{memo_id} not found."
    
    tags_str = ", ".join(memo.tags) if memo.tags else "None"
    return (
        f"# Memo #{memo.id}: {memo.title}\n"
        f"**Category:** {memo.category} | **Tags:** {tags_str}\n"
        f"**Created:** {memo.created_at}\n\n"
        f"{memo.content}"
    )


@server.tool(
    name="search_memos",
    description="Search memos by keyword across title, content, tags, and category."
)
def search_memos(query: str) -> str:
    """Search memos by text."""
    results = store.search(query)
    if not results:
        return f"No memos matching '{query}'."

    lines = [f"Found {len(results)} memo(s) matching '{query}':"]
    for m in results:
        lines.append(f"- [#{m.id}] **{m.title}** [{m.category}] -> {m.content}")
    return "\n".join(lines)


@server.tool(
    name="delete_memo",
    description="Delete a specific memo by ID."
)
def delete_memo(memo_id: str) -> str:
    """Delete a memo."""
    success = store.delete(memo_id.strip())
    if success:
        return f"Memo #{memo_id} successfully deleted."
    return f"Error: Memo #{memo_id} not found."


@server.tool(
    name="clear_memos",
    description="Clear all stored memos (use with caution)."
)
def clear_memos() -> str:
    """Clear all memos."""
    count = store.clear()
    return f"Cleared {count} memo(s)."


# ============================================================================
# MCP RESOURCES
# ============================================================================

@server.resource(
    "memo://all",
    description="Dynamic markdown digest of all stored memos."
)
def get_all_memos_resource() -> str:
    """Return all memos in formatted markdown."""
    memos = store.list_all()
    if not memos:
        return "# QuickMemo Digest\n\n*No memos currently stored.*"

    lines = ["# QuickMemo Digest", f"*Total Memos:* {len(memos)}\n"]
    for m in memos:
        tags_str = f" `[{', '.join(m.tags)}]`" if m.tags else ""
        lines.append(f"## #{m.id} - {m.title} ({m.category}){tags_str}")
        lines.append(f"*Created: {m.created_at}*\n")
        lines.append(f"{m.content}\n")
        lines.append("---")
    return "\n".join(lines)


@server.resource(
    "memo://stats",
    description="Real-time statistics and summary metrics for QuickMemo."
)
def get_memo_stats_resource() -> str:
    """Return metrics on stored memos."""
    memos = store.list_all()
    categories: Dict[str, int] = {}
    tags: Dict[str, int] = {}

    for m in memos:
        categories[m.category] = categories.get(m.category, 0) + 1
        for t in m.tags:
            tags[t] = tags.get(t, 0) + 1

    return json.dumps({
        "total_memos": len(memos),
        "categories": categories,
        "tags": tags,
        "storage_path": str(store.file_path)
    }, indent=2)


# ============================================================================
# MCP PROMPTS
# ============================================================================

@server.prompt(
    name="review_notes",
    description="Generate a synthesis, key takeaways, and action items from saved memos."
)
def review_notes(category: str = "") -> str:
    """Generate a prompt to review and summarize memos."""
    memos = store.list_all(category=category if category else None)
    if not memos:
        return "No memos found to review. Please add some memos first."

    memo_texts = "\n\n".join([f"- **[#{m.id}] {m.title}** ({m.category}):\n{m.content}" for m in memos])
    return (
        f"You are reviewing the following context memos (Filter: {category or 'All'}):\n\n"
        f"{memo_texts}\n\n"
        f"Please provide:\n"
        f"1. A concise synthesis of the key themes.\n"
        f"2. Practical takeaways and insights.\n"
        f"3. A prioritized action checklist based on these notes."
    )


@server.prompt(
    name="daily_standup",
    description="Generate a structured daily standup update from today's context memos."
)
def daily_standup() -> str:
    """Generate a daily standup prompt from stored memos."""
    memos = store.list_all()
    memo_texts = "\n\n".join([f"- [#{m.id}] {m.title} [{m.category}]: {m.content}" for m in memos[:10]])
    return (
        f"Here are recent developer memos and activities:\n\n"
        f"{memo_texts}\n\n"
        f"Generate a crisp daily standup update with the standard 3 sections:\n"
        f"1. **What was worked on / captured**\n"
        f"2. **Key findings or active blockers**\n"
        f"3. **Next planned steps**"
    )


def main() -> None:
    """CLI entry point for QuickMemo MCP server."""
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
