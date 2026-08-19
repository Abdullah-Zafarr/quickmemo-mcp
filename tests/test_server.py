"""Unit and integration tests for QuickMemo MCP Server."""

import json
import pytest
from pathlib import Path
from quickmemo.server import (
    MemoStore,
    add_memo,
    list_memos,
    get_memo,
    search_memos,
    delete_memo,
    clear_memos,
    get_all_memos_resource,
    get_memo_stats_resource,
    review_notes,
    daily_standup,
    store as global_store,
)


@pytest.fixture(autouse=True)
def isolated_store(tmp_path: Path):
    """Fixture to provide a clean temporary storage file for every test."""
    temp_file = tmp_path / "test_memos.json"
    test_store = MemoStore(file_path=temp_file)
    
    # Patch the global store used by server tool functions
    global_store.file_path = temp_file
    global_store._save({})
    yield test_store


class TestMemoStore:
    def test_add_and_get(self, isolated_store: MemoStore):
        memo = isolated_store.add(
            title="MCP Protocol Research",
            content="Learned about stdio JSON-RPC transport and FastMCP.",
            category="learning",
            tags=["mcp", "python"]
        )
        assert memo.id is not None
        assert memo.title == "MCP Protocol Research"
        assert memo.category == "learning"
        assert memo.tags == ["mcp", "python"]

        retrieved = isolated_store.get(memo.id)
        assert retrieved is not None
        assert retrieved.title == memo.title
        assert retrieved.content == memo.content

    def test_list_and_filter(self, isolated_store: MemoStore):
        isolated_store.add("Note 1", "Content 1", category="work", tags=["urgent"])
        isolated_store.add("Note 2", "Content 2", category="personal", tags=["ideas"])
        isolated_store.add("Note 3", "Content 3", category="work", tags=["ideas"])

        all_memos = isolated_store.list_all()
        assert len(all_memos) == 3

        work_memos = isolated_store.list_all(category="work")
        assert len(work_memos) == 2

        idea_memos = isolated_store.list_all(tag="ideas")
        assert len(idea_memos) == 2

    def test_search(self, isolated_store: MemoStore):
        isolated_store.add("Bug in Auth API", "Token verification fails on expired JWT", category="bugs")
        isolated_store.add("Recipe", "Pasta carbonara ingredients", category="food")

        results = isolated_store.search("token")
        assert len(results) == 1
        assert results[0].title == "Bug in Auth API"

        results_category = isolated_store.search("food")
        assert len(results_category) == 1

    def test_delete_and_clear(self, isolated_store: MemoStore):
        m1 = isolated_store.add("Temp Note", "To be deleted")
        assert isolated_store.delete(m1.id) is True
        assert isolated_store.get(m1.id) is None
        assert isolated_store.delete("non-existent") is False

        isolated_store.add("Keep 1", "Text")
        isolated_store.add("Keep 2", "Text")
        cleared_count = isolated_store.clear()
        assert cleared_count == 2
        assert len(isolated_store.list_all()) == 0


class TestServerTools:
    def test_tool_workflow(self):
        # 1. Add Memo
        add_res = add_memo(
            title="FastMCP Architecture",
            content="FastMCP simplifies tool, resource, and prompt registration.",
            category="mcp",
            tags=["architecture", "sdk"]
        )
        assert "Created Memo #" in add_res
        assert "FastMCP Architecture" in add_res

        # 2. List Memos
        list_res = list_memos()
        assert "Found 1 memo(s)" in list_res
        assert "FastMCP Architecture" in list_res

        # Extract ID from response (e.g. #abc12345)
        import re
        match = re.search(r"#([a-f0-9]+)", add_res)
        assert match is not None
        memo_id = match.group(1)

        # 3. Get Memo
        get_res = get_memo(memo_id)
        assert f"Memo #{memo_id}" in get_res
        assert "FastMCP Architecture" in get_res

        # 4. Search Memos
        search_res = search_memos("architecture")
        assert "Found 1 memo(s)" in search_res

        # 5. Delete Memo
        del_res = delete_memo(memo_id)
        assert "successfully deleted" in del_res

        # Verify empty
        empty_list = list_memos()
        assert "No memos found" in empty_list

    def test_clear_memos_tool(self):
        add_memo("A", "Content A")
        add_memo("B", "Content B")
        res = clear_memos()
        assert "Cleared 2 memo(s)" in res
        assert "No memos found" in list_memos()


class TestServerResourcesAndPrompts:
    def test_resources(self):
        add_memo("Docker Tip", "Use multi-stage builds for small images", category="devops", tags=["docker"])
        
        # Test memo://all resource
        digest = get_all_memos_resource()
        assert "# QuickMemo Digest" in digest
        assert "Docker Tip" in digest
        assert "devops" in digest

        # Test memo://stats resource
        stats_raw = get_memo_stats_resource()
        stats = json.loads(stats_raw)
        assert stats["total_memos"] == 1
        assert stats["categories"]["devops"] == 1
        assert stats["tags"]["docker"] == 1

    def test_prompts(self):
        add_memo("Task 1", "Implement JSON-RPC serializer", category="dev")
        add_memo("Task 2", "Write unit test suite", category="dev")

        # Test review_notes prompt
        review_prompt = review_notes(category="dev")
        assert "Task 1" in review_prompt
        assert "Task 2" in review_prompt
        assert "prioritized action checklist" in review_prompt

        # Test daily_standup prompt
        standup_prompt = daily_standup()
        assert "Task 1" in standup_prompt
        assert "daily standup update" in standup_prompt
