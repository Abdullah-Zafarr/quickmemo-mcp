"""Functional tests for VaultCraft MCP Server tools, resources, and prompts."""

import json
import os
import shutil
import tempfile
import pytest

from vaultcraft.server import (
    mcp,
    storage,
    create_or_update_note,
    read_note,
    search_vault,
    find_backlinks,
    get_graph_metrics,
    log_daily_entry,
    delete_note,
    get_note_resource,
    get_today_daily_resource,
    get_graph_overview_resource,
    synthesize_concept,
    daily_standup,
    knowledge_gap_analysis,
)
from vaultcraft.storage import VaultStorage


@pytest.fixture(autouse=True)
def setup_clean_vault(monkeypatch):
    """Sets up an isolated temporary vault for every test."""
    temp_dir = tempfile.mkdtemp()
    temp_storage = VaultStorage(root_dir=temp_dir)
    # Monkeypatch storage in server module
    import vaultcraft.server as srv_mod
    monkeypatch.setattr(srv_mod, "storage", temp_storage)
    yield temp_storage
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_tool_create_and_read_note():
    res = create_or_update_note(
        title="Zettelkasten Method",
        content="The Zettelkasten method utilizes [[Atomic Notes]] and [[Bidirectional Links]].",
        tags=["pkm", "productivity"]
    )
    assert "saved successfully" in res
    assert "[[Atomic Notes]]" in res

    read_res = read_note("Zettelkasten Method")
    assert "# Zettelkasten Method" in read_res
    assert "pkm" in read_res
    assert "[[Atomic Notes]]" in read_res


def test_tool_search_and_backlinks():
    create_or_update_note("Smart Notes", "Book by Ahrens on [[Zettelkasten Method]].", ["books"])
    create_or_update_note("Zettelkasten Method", "Core knowledge management system.", ["pkm"])

    search_res = search_vault(query="Ahrens")
    assert "Smart Notes" in search_res

    backlinks_res = find_backlinks("Zettelkasten Method")
    assert "Smart Notes" in backlinks_res


def test_tool_metrics_and_delete():
    create_or_update_note("Node A", "Links to [[Node B]].", ["graph"])
    create_or_update_note("Node B", "Target node.", ["graph"])
    create_or_update_note("Node Orphan", "Lonely node.", ["lonely"])

    metrics_res = get_graph_metrics()
    assert "Total Notes: 3" in metrics_res
    assert "[[Node Orphan]]" in metrics_res

    del_res = delete_note("Node Orphan")
    assert "Successfully deleted" in del_res

    not_found = read_note("Node Orphan")
    assert "not found" in not_found


def test_tool_daily_entry():
    log_res = log_daily_entry("Shipped VaultCraft MCP server v1.0", category="Release")
    assert "Logged entry" in log_res

    daily_resource = get_today_daily_resource()
    assert "Shipped VaultCraft MCP server v1.0" in daily_resource
    assert "Release" in daily_resource


def test_resources():
    create_or_update_note("Resource Test Note", "Raw content payload.", ["test"])
    
    note_content = get_note_resource("Resource Test Note")
    assert "Resource Test Note" in note_content
    assert "Raw content payload." in note_content

    graph_overview = get_graph_overview_resource()
    parsed = json.loads(graph_overview)
    assert parsed["total_notes"] == 1


def test_prompts():
    create_or_update_note("FastMCP Notes", "FastMCP simplifies creating Python MCP tools.", ["mcp"])
    
    prompt_synth = synthesize_concept(tag="mcp", objective="Understand FastMCP")
    assert "FastMCP Notes" in prompt_synth
    assert "Understand FastMCP" in prompt_synth

    prompt_standup = daily_standup()
    assert "Accomplishments" in prompt_standup

    prompt_gaps = knowledge_gap_analysis()
    assert "FastMCP Notes" in prompt_gaps
