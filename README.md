# QuickMemo MCP Server 📝⚡

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-2.0-orange.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Smithery Ready](https://img.shields.io/badge/Smithery-Compatible-success.svg)](https://smithery.ai/)
[![Tests](https://img.shields.io/badge/tests-8%20passed-brightgreen.svg)](tests/)

**QuickMemo MCP** is a sleek, minimalistic, and unique Model Context Protocol (MCP) server that provides AI assistants with a fast, structured scratchpad and context memo engine.

Built cleanly using the official Python MCP SDK, QuickMemo showcases all **three core MCP primitives**—**Tools**, **Resources**, and **Prompts**—in an elegant, zero-bloat codebase

---

## 🌟 Key Highlights

- ⚡ **Minimalist & Zero-Bloat**: Under 150 lines of clean, readable Python code.
- 🎯 **All 3 MCP Primitives**:
  - **Tools**: Save, list, search, filter, retrieve, and delete context memos.
  - **Resources**: Real-time markdown digest (`memo://all`) and dynamic telemetry (`memo://stats`).
  - **Prompts**: Ready-to-use prompt templates for note reviews and daily standup generation.
- 🔒 **Zero Configuration Required**: Uses local persistent JSON storage (`~/.quickmemo/memos.json` or custom path).
- 🚀 **Marketplace & Registry Ready**: Preconfigured with `smithery.yaml` and `Dockerfile` for one-click deployment to Smithery and Glama.

---

## 📁 Project Structure

```
quickmemo-mcp/
├── docs/                               # Learning documentation & reports
│   ├── EXISTING_MCP_EXPERIENCE.md      # Hands-on write-up evaluating Context7 & Playwright
│   └── MCP_FUNDAMENTALS.md             # Complete MCP protocol & architecture guide
├── src/
│   └── quickmemo/                      # MCP Server package (<150 LOC)
│       ├── __init__.py                 # Package exports
│       ├── __main__.py                 # Executable entrypoint
│       └── server.py                   # Core server (Tools, Resources, Prompts)
├── tests/
│   ├── demo_client.py                  # Live interactive demonstration script
│   └── test_server.py                  # Pytest unit & integration test suite
├── Dockerfile                          # Containerized deployment manifest
├── LICENSE                             # MIT License
├── pyproject.toml                      # Package configuration & dependencies
├── README.md                           # Quickstart & user documentation
└── smithery.yaml                       # Smithery registry manifest
```

---

## 📐 Architecture Overview

```
+-------------------------------------------------------------------------------+
|                                  MCP CLIENT                                   |
|             (Claude Desktop / Cursor IDE / Antigravity / Custom AI)           |
+-------------------------------------------------------------------------------+
                                       ▲
                                       │ JSON-RPC 2.0 (stdio)
                                       ▼
+-------------------------------------------------------------------------------+
|                             QUICKMEMO MCP SERVER                              |
|                                                                               |
|   [TOOLS]                     [RESOURCES]                 [PROMPTS]           |
|   • add_memo                  • memo://all (Digest)       • review_notes      |
|   • list_memos                • memo://stats (JSON)       • daily_standup     |
|   • search_memos                                                              |
|   • get_memo / delete_memo                                                    |
+-------------------------------------------------------------------------------+
                                       │
                                       ▼
                         Local JSON Storage Engine
                         (~/.quickmemo/memos.json)
```

---

## 🛠️ MCP Primitives Catalog

### 1. Tools (Model-Controlled Functions)

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `add_memo` | `title: str`, `content: str`, `category?: str`, `tags?: list[str]` | Saves a new memo or snippet with optional category and tags. |
| `list_memos` | `category?: str`, `tag?: str` | Lists saved memos with optional category and tag filtering. |
| `get_memo` | `memo_id: str` | Retrieves full content and metadata for a specific memo. |
| `search_memos` | `query: str` | Performs keyword search across title, content, tags, and category. |
| `delete_memo` | `memo_id: str` | Deletes a memo by ID. |
| `clear_memos` | *None* | Empties the memo store. |

### 2. Resources (Dynamic Context Streams)

| Resource URI | MIME Type | Description |
| :--- | :--- | :--- |
| `memo://all` | `text/markdown` | Formatted dynamic markdown digest of all stored memos. |
| `memo://stats` | `application/json` | Real-time statistics (total memos, categories breakdown, tag distribution). |

### 3. Prompts (Pre-Engineered Workflow Templates)

| Prompt Name | Arguments | Description |
| :--- | :--- | :--- |
| `review_notes` | `category?: str` | Synthesizes saved memos into key takeaways and an actionable checklist. |
| `daily_standup` | *None* | Converts recent memos into a standard 3-part daily standup report. |

---

## 🚀 Quickstart & Installation

### Option 1: Local Setup with `uv` (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/quickmemo-mcp.git
cd quickmemo-mcp

# Install dependencies and package in editable mode
uv pip install -e .

# Run test suite
uv run pytest -v

# Run the interactive demo
uv run python tests/demo_client.py
```

### Option 2: Running Directly via CLI

```bash
# Run server over stdio
quickmemo
```

---

## 🔌 Client Configuration

### Claude Desktop
Add QuickMemo to your `claude_desktop_config.json`:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "quickmemo": {
      "command": "uvx",
      "args": ["--from", "quickmemo", "quickmemo"]
    }
  }
}
```

### Cursor IDE
Add to `.cursor/mcp.json` in your workspace:

```json
{
  "mcpServers": {
    "quickmemo": {
      "command": "quickmemo"
    }
  }
}
```

---

## ☁️ Deploying to Smithery / Glama

This repository is pre-configured for the **Smithery** registry with `smithery.yaml` and `Dockerfile`.

### Install via Smithery CLI
```bash
npx -y @smithery/cli install quickmemo --client claude
```

### Manual Registry Deployment
1. Push your repository to GitHub.
2. Visit [Smithery.ai](https://smithery.ai) and sign in.
3. Import your GitHub repository. Smithery automatically detects `smithery.yaml` and deploys your MCP server.

---

## 🧪 Testing

Run the automated test suite:
```bash
uv run pytest -v
```

Output:
```
tests/test_server.py::TestMemoStore::test_add_and_get PASSED             [ 12%]
tests/test_server.py::TestMemoStore::test_list_and_filter PASSED         [ 25%]
tests/test_server.py::TestMemoStore::test_search PASSED                  [ 37%]
tests/test_server.py::TestMemoStore::test_delete_and_clear PASSED        [ 50%]
tests/test_server.py::TestServerTools::test_tool_workflow PASSED         [ 62%]
tests/test_server.py::TestServerTools::test_clear_memos_tool PASSED      [ 75%]
tests/test_server.py::TestServerResourcesAndPrompts::test_resources PASSED [ 87%]
tests/test_server.py::TestServerResourcesAndPrompts::test_prompts PASSED [100%]

============================== 8 passed in 1.10s ==============================
```

---

## 📚 Deliverables & Learning Documentation

- 📖 **Existing MCP Hands-On Evaluation**: [`docs/EXISTING_MCP_EXPERIENCE.md`](docs/EXISTING_MCP_EXPERIENCE.md)
- 📘 **MCP Architecture & Fundamentals Guide**: [`docs/MCP_FUNDAMENTALS.md`](docs/MCP_FUNDAMENTALS.md)
- 💻 **Interactive Live Demo Script**: [`tests/demo_client.py`](tests/demo_client.py)
- ⚙️ **Smithery Configuration**: [`smithery.yaml`](smithery.yaml)

---

## 📄 License

MIT License © 2026 QuickMemo MCP Contributors.

