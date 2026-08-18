# 🏛️ VaultCraft MCP

[![Smithery Badge](https://smithery.ai/badge/vaultcraft)](https://smithery.ai/server/vaultcraft)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Protocol 2.0](https://img.shields.io/badge/MCP-Protocol%202.0-purple.svg)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**VaultCraft MCP** is a high-performance, local-first Model Context Protocol (MCP) server that empowers AI assistants with structured **Zettelkasten knowledge management**, **bidirectional `[[wikilink]]` graphs**, and a **daily developer journal**.

---

## 🌟 Key Capabilities

VaultCraft implements all three core primitives of the Model Context Protocol:

- 🛠️ **7 MCP Tools**: Create atomic markdown notes with YAML frontmatter, search across concepts with relevance scoring, resolve bidirectional backlinks, compute knowledge graph connectivity metrics, and log daily developer activities.
- 📦 **3 Dynamic MCP Resources**: Directly stream raw note markdown (`vault://notes/{title}`), live daily journal (`vault://daily/today`), and JSON graph analytics (`vault://graph/overview`).
- 💡 **3 Custom MCP Prompts**: Instant workflows for concept synthesis, daily standup generation, and knowledge-gap link recommendation.

---

## 📋 MCP Interface Reference

### 1. Tools

| Tool | Parameters | Description |
| :--- | :--- | :--- |
| `create_or_update_note` | `title: str`, `content: str`, `tags?: list[str]` | Creates or updates an atomic note with YAML frontmatter and extracts `[[wikilinks]]`. |
| `read_note` | `title: str` | Retrieves full markdown content, metadata, outgoing links, and inbound backlinks. |
| `search_vault` | `query?: str`, `tag?: str`, `limit?: int` | Searches note titles, bodies, and tags with relevance scoring. |
| `find_backlinks` | `title: str` | Finds all notes linking to the target concept via `[[wikilinks]]`. |
| `get_graph_metrics` | *None* | Analyzes graph health, total links, tag frequencies, and orphan notes. |
| `log_daily_entry` | `entry: str`, `category?: str` | Appends timestamped log entry to today's markdown journal (`daily/YYYY-MM-DD.md`). |
| `delete_note` | `title: str` | Deletes a note and updates references. |

### 2. Resources

| Resource URI | MIME Type | Description |
| :--- | :--- | :--- |
| `vault://notes/{title}` | `text/markdown` | Direct markdown stream for any note in the vault. |
| `vault://daily/today` | `text/markdown` | Real-time content of today's developer journal. |
| `vault://graph/overview` | `application/json` | JSON graph metrics (total notes, links, tags, orphan notes). |

### 3. Prompts

| Prompt Name | Arguments | Description |
| :--- | :--- | :--- |
| `synthesize_concept` | `tag: str`, `objective?: str` | Aggregates all notes for a tag and synthesizes a comprehensive concept briefing. |
| `daily_standup` | `date_str?: str` | Converts daily journal entries into a clean 3-part standup update. |
| `knowledge_gap_analysis` | *None* | Evaluates isolated notes and suggests new bridging `[[wikilinks]]`. |

---

## 🚀 Quickstart & Installation

### Option 1: Install via Smithery (Recommended)

To install VaultCraft for Claude Desktop automatically via [Smithery](https://smithery.ai/):

```bash
npx -y @smithery/cli install vaultcraft --client claude
```

---

### Option 2: Local Installation with `uv`

```bash
# Clone the repository
git clone https://github.com/your-username/vaultcraft-mcp.git
cd vaultcraft-mcp

# Create virtual environment and install
uv venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
uv pip install -e .
```

---

### Option 3: Run with Docker

```bash
docker build -t vaultcraft-mcp .
docker run -i --rm -v $(pwd)/.vaultcraft_data:/data/vault vaultcraft-mcp
```

---

## ⚙️ Client Configurations

### Claude Desktop Configuration

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "vaultcraft": {
      "command": "uvx",
      "args": ["--from", "vaultcraft", "vaultcraft"],
      "env": {
        "VAULTCRAFT_PATH": "C:/Users/YourName/Documents/MyVault"
      }
    }
  }
}
```

*Or for direct local development:*

```json
{
  "mcpServers": {
    "vaultcraft": {
      "command": "python",
      "args": ["-m", "vaultcraft"],
      "cwd": "C:/path/to/vaultcraft-mcp"
    }
  }
}
```

---

### Cursor Configuration

In Cursor Settings $\rightarrow$ Features $\rightarrow$ MCP Servers $\rightarrow$ Add New MCP Server:
- **Name**: `vaultcraft`
- **Type**: `command`
- **Command**: `uv run vaultcraft`

---

### MCP Inspector (Interactive Visual Debugger)

Test tools, resources, and prompt schemas directly in your browser:

```bash
npx @modelcontextprotocol/inspector uv run vaultcraft
```

---

## 🧪 Testing

Run the automated test suite with pytest:

```bash
pytest tests/
```

Run the end-to-end interactive demo client:

```bash
python tests/test_client_interactive.py
```

---

## 📚 Deliverables & Documentation

- 📘 [Playwright MCP Exploration Experience Report](PLAYWRIGHT_MCP_EXPERIENCE.md)
- 📗 [MCP Fundamentals & Architecture Guide](MCP_FUNDAMENTALS.md)
- ⚙️ [Smithery Manifest](smithery.yaml)

---

## 📄 License

MIT License - feel free to use and extend for personal or commercial projects.
