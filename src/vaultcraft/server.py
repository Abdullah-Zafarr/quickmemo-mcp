"""MCP Server Implementation for VaultCraft."""

import json
from typing import List, Optional

try:
    from mcp.server import MCPServer
except ImportError:
    from mcp.server.fastmcp import FastMCP as MCPServer

from .storage import VaultStorage

# Initialize MCP Server App
mcp = MCPServer(name="VaultCraft")

storage = VaultStorage()


# ============================================================================
# MCP TOOLS
# ============================================================================

@mcp.tool()
def create_or_update_note(
    title: str,
    content: str,
    tags: Optional[List[str]] = None,
) -> str:
    """Create a new markdown note or update an existing one in the Zettelkasten vault.
    
    Supports bidirectional [[wikilinks]] inside the content body (e.g. 'See [[Architecture]] for details').
    
    Args:
        title: The unique title of the note (e.g., 'Model Context Protocol').
        content: The markdown body of the note.
        tags: Optional list of categorization tags (e.g., ['mcp', 'architecture', 'ai']).
    """
    note = storage.save_note(title=title, content=content, tags=tags or [])
    outgoing_str = ", ".join([f"[[{l}]]" for l in note.metadata.outgoing_links]) or "None"
    return (
        f"✅ Note '{note.title}' saved successfully.\n"
        f"• Tags: {', '.join(note.metadata.tags) or 'None'}\n"
        f"• Outgoing Wikilinks: {outgoing_str}\n"
        f"• Updated At: {note.metadata.updated_at}"
    )


@mcp.tool()
def read_note(title: str) -> str:
    """Retrieve full content and metadata for a specific note in the vault.
    
    Args:
        title: The title or topic of the note to read.
    """
    note = storage.read_note(title)
    if not note:
        return f"❌ Note '{title}' not found in the vault."

    backlinks = storage.find_backlinks(title)
    backlinks_str = ", ".join([f"[[{b}]]" for b in backlinks]) or "None"

    return (
        f"# {note.title}\n\n"
        f"**Metadata:**\n"
        f"- Tags: {', '.join(note.metadata.tags) or 'None'}\n"
        f"- Created: {note.metadata.created_at}\n"
        f"- Outgoing Links: {', '.join(note.metadata.outgoing_links) or 'None'}\n"
        f"- Inbound Backlinks: {backlinks_str}\n\n"
        f"---\n\n"
        f"{note.content}"
    )


@mcp.tool()
def search_vault(
    query: str = "",
    tag: str = "",
    limit: int = 5,
) -> str:
    """Search through note titles, contents, and tags across the knowledge vault.
    
    Args:
        query: Keywords or phrases to match against note titles and text.
        tag: Filter results by a specific tag (e.g., 'architecture').
        limit: Maximum number of search results to return (default: 5).
    """
    results = storage.search(query=query, tag=tag, limit=limit)
    if not results:
        return f"🔍 No notes found matching query='{query}' tag='{tag}'."

    output = [f"🔍 Found {len(results)} note(s):\n"]
    for idx, r in enumerate(results, 1):
        tags_str = f" [Tags: {', '.join(r['tags'])}]" if r['tags'] else ""
        output.append(f"{idx}. **{r['title']}** (Score: {r['score']}){tags_str}")
        output.append(f"   Snippet: {r['snippet']}")
        if r['outgoing_links']:
            output.append(f"   Links: {', '.join([f'[[{l}]]' for l in r['outgoing_links']])}")
        output.append("")

    return "\n".join(output)


@mcp.tool()
def find_backlinks(title: str) -> str:
    """Find all other notes in the vault that link to the specified note via [[wikilinks]].
    
    Args:
        title: The title of the target note to find inbound references for.
    """
    backlinks = storage.find_backlinks(title)
    if not backlinks:
        return f"🔗 No notes currently link to '[[{title}]]'."

    links_list = "\n".join([f"- [[{b}]]" for b in backlinks])
    return f"🔗 Found {len(backlinks)} note(s) linking to '[[{title}]]':\n{links_list}"


@mcp.tool()
def get_graph_metrics() -> str:
    """Analyze the knowledge vault graph health, link density, tag distribution, and orphan notes.
    
    Use this to identify isolated knowledge islands or heavily referenced hub topics.
    """
    metrics = storage.get_metrics()
    
    top_hubs = "\n".join([f"- **{h['title']}**: {h['backlinks']} incoming references" for h in metrics.most_linked_notes]) or "None yet"
    orphans = ", ".join([f"[[{o}]]" for o in metrics.orphan_notes]) or "None (All notes are interconnected!)"
    tags = ", ".join([f"#{k} ({v})" for k, v in metrics.tags.items()]) or "None"

    return (
        f"📊 **VaultCraft Knowledge Graph Metrics**\n\n"
        f"• Total Notes: {metrics.total_notes}\n"
        f"• Total Wikilinks: {metrics.total_links}\n"
        f"• Total Unique Tags: {metrics.total_tags}\n\n"
        f"**Top Hub Notes:**\n{top_hubs}\n\n"
        f"**Orphan Notes (Isolated):**\n{orphans}\n\n"
        f"**Tag Cloud:**\n{tags}"
    )


@mcp.tool()
def log_daily_entry(entry: str, category: str = "General") -> str:
    """Append a timestamped entry to today's daily journal log.
    
    Args:
        entry: The text or markdown description of the task, meeting, idea, or achievement.
        category: Category label (e.g., 'Standup', 'BugFix', 'Idea', 'Meeting', 'Learning').
    """
    result = storage.append_daily_log(entry=entry, category=category)
    return f"📝 {result}"


@mcp.tool()
def delete_note(title: str) -> str:
    """Delete a note from the vault.
    
    Args:
        title: The title of the note to delete.
    """
    deleted = storage.delete_note(title)
    if deleted:
        return f"🗑️ Successfully deleted note '{title}'."
    return f"❌ Note '{title}' does not exist in the vault."


# ============================================================================
# MCP RESOURCES
# ============================================================================

@mcp.resource("vault://notes/{title}")
def get_note_resource(title: str) -> str:
    """Dynamic resource: Retrieve raw markdown content for any note in the vault."""
    note = storage.read_note(title)
    if not note:
        return f"# Note Not Found\n\nNote '{title}' does not exist in the vault."
    return note.raw_markdown


@mcp.resource("vault://daily/today")
def get_today_daily_resource() -> str:
    """Dynamic resource: Retrieve today's daily developer journal."""
    return storage.read_daily_log()


@mcp.resource("vault://graph/overview")
def get_graph_overview_resource() -> str:
    """Dynamic resource: JSON summary of all notes, connectivity, and tags."""
    metrics = storage.get_metrics()
    return json.dumps(metrics.model_dump(), indent=2)


# ============================================================================
# MCP PROMPTS
# ============================================================================

@mcp.prompt()
def synthesize_concept(tag: str, objective: str = "Synthesize key insights") -> str:
    """Prompt template: Gather all notes with a specific tag and synthesize comprehensive insights."""
    notes = storage.list_all_notes()
    matching_notes = [n for n in notes if tag.lower() in [t.lower() for t in n.metadata.tags]]
    
    context_chunks = []
    for n in matching_notes:
        context_chunks.append(f"### Note: {n.title}\n{n.content}\n")

    context_str = "\n".join(context_chunks) if context_chunks else "No notes found matching this tag."

    return (
        f"You are an expert knowledge synthesizer analyzing a personal Zettelkasten vault.\n\n"
        f"Objective: {objective}\n"
        f"Target Topic Tag: #{tag}\n\n"
        f"Here are the existing notes from the vault:\n\n"
        f"{context_str}\n\n"
        f"Instructions:\n"
        f"1. Synthesize the core concepts, identifying patterns and common themes across the notes.\n"
        f"2. Point out any contradictions or unanswered questions.\n"
        f"3. Propose 2-3 new atomic notes to create next with suggested [[wikilinks]]."
    )


@mcp.prompt()
def daily_standup(date_str: str = "") -> str:
    """Prompt template: Analyze daily journal entries and generate a crisp standup summary."""
    journal_text = storage.read_daily_log(date_str if date_str else None)
    
    return (
        f"You are an executive assistant preparing a daily standup update based on the developer's journal.\n\n"
        f"Journal Entries:\n{journal_text}\n\n"
        f"Please organize this into a clean 3-part update:\n"
        f"1. 🚀 **Accomplishments & Completed Work**\n"
        f"2. 🚧 **Blockers, Challenges & Open Questions**\n"
        f"3. 🎯 **Next Priorities for Tomorrow**"
    )


@mcp.prompt()
def knowledge_gap_analysis() -> str:
    """Prompt template: Review orphan notes and isolated clusters to suggest missing links and ideas."""
    metrics = storage.get_metrics()
    notes = storage.list_all_notes()
    
    notes_summary = "\n".join([f"- **{n.title}** (Tags: {', '.join(n.metadata.tags)}) -> Outgoing: {n.metadata.outgoing_links}" for n in notes])
    
    return (
        f"You are a Zettelkasten architecture specialist optimizing knowledge graph density.\n\n"
        f"Vault Summary:\n"
        f"• Total Notes: {metrics.total_notes}\n"
        f"• Orphan Notes: {metrics.orphan_notes}\n\n"
        f"Current Notes in Vault:\n"
        f"{notes_summary}\n\n"
        f"Please analyze this graph and provide:\n"
        f"1. High-value [[wikilinks]] that should be added between existing notes.\n"
        f"2. Bridge topics: 1-2 new note ideas that would connect isolated concepts.\n"
        f"3. Action items to eliminate orphan notes."
    )


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

def main():
    """Runs the VaultCraft MCP server over stdio transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
