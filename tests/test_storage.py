"""Unit tests for VaultStorage engine."""

import shutil
import tempfile
from pathlib import Path
import pytest

from vaultcraft.storage import VaultStorage


@pytest.fixture
def temp_vault():
    temp_dir = tempfile.mkdtemp()
    storage = VaultStorage(root_dir=temp_dir)
    yield storage
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_save_and_read_note(temp_vault: VaultStorage):
    note = temp_vault.save_note(
        title="Model Context Protocol",
        content="MCP standardizes context sharing for [[LLM Architecture]] and [[AI Tools]].",
        tags=["mcp", "protocol"]
    )
    assert note.title == "Model Context Protocol"
    assert "mcp" in note.metadata.tags
    assert "LLM Architecture" in note.metadata.outgoing_links
    assert "AI Tools" in note.metadata.outgoing_links

    read = temp_vault.read_note("Model Context Protocol")
    assert read is not None
    assert read.title == "Model Context Protocol"
    assert "protocol" in read.metadata.tags


def test_backlinks_and_graph_metrics(temp_vault: VaultStorage):
    temp_vault.save_note("Python SDK", "Used for building [[VaultCraft MCP]] tools.", ["python"])
    temp_vault.save_note("FastMCP", "High-level interface in the [[Python SDK]].", ["fastmcp"])
    temp_vault.save_note("VaultCraft MCP", "Personal Zettelkasten knowledge vault.", ["vaultcraft"])
    temp_vault.save_note("Isolated Concept", "No links here.", ["isolated"])

    # Backlinks test
    backlinks = temp_vault.find_backlinks("Python SDK")
    assert "FastMCP" in backlinks

    backlinks_vaultcraft = temp_vault.find_backlinks("VaultCraft MCP")
    assert "Python SDK" in backlinks_vaultcraft

    # Metrics test
    metrics = temp_vault.get_metrics()
    assert metrics.total_notes == 4
    assert metrics.total_links == 2
    assert "Isolated Concept" in metrics.orphan_notes


def test_search_notes(temp_vault: VaultStorage):
    temp_vault.save_note("FastAPI Guide", "Async framework for building web APIs.", ["web", "api"])
    temp_vault.save_note("FastMCP Guide", "Build MCP servers quickly in Python.", ["mcp", "sdk"])

    res = temp_vault.search(query="FastMCP")
    assert len(res) >= 1
    assert res[0]["title"] == "FastMCP Guide"

    tag_res = temp_vault.search(tag="api")
    assert len(tag_res) >= 1
    assert tag_res[0]["title"] == "FastAPI Guide"


def test_daily_log(temp_vault: VaultStorage):
    res = temp_vault.append_daily_log("Completed MCP testing and unit tests.", category="Testing")
    assert "Logged entry" in res
    log_content = temp_vault.read_daily_log()
    assert "Completed MCP testing and unit tests." in log_content
    assert "Testing" in log_content
