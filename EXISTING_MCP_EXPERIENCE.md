# Hands-On Exploration & Experience Report: Existing MCP Servers

**Author:** Antigravity Engineering Task  
**Focus:** Exploring, Testing, and Evaluating Existing Model Context Protocol (MCP) Servers  
**Target MCPs:** `Context7 MCP` (Real-time Documentation Extraction) & `Playwright / Chrome DevTools MCP` (Browser Automation)  

---

## 1. Executive Summary

As part of the MCP onboarding milestone, we explored, installed, and evaluated existing MCP servers from the **Smithery** and **Glama** registries. We tested two prominent MCP implementations:

1. **Context7 MCP** — A documentation and context resolution MCP server enabling LLMs to fetch up-to-date documentation and code samples directly from official sources.
2. **Playwright / Chrome DevTools MCP** — A browser engine MCP server allowing LLMs to inspect DOM structures, evaluate JavaScript, interact with web elements, and take visual screenshots.

This write-up documents what these servers do, how they communicate via the Model Context Protocol, how they were useful in practice, and the design principles we carried forward when building **QuickMemo MCP**.

---

## 2. Deep Dive: Context7 MCP

### What Does Context7 Do?
Modern software libraries evolve rapidly, often outdating the static training cutoff of LLMs. **Context7** bridges this gap by exposing specialized MCP tools to resolve library IDs and query authoritative, version-specific documentation dynamically.

```
+-------------+      MCP JSON-RPC (stdio)      +-------------------+      HTTPS Query      +--------------------+
|  MCP Client | <============================> |   Context7 MCP    | <===================> | Official Up-to-Date|
| (LLM Agent) |    tools/call "query-docs"     |     Server        |   (Markdown Parser)   |   Documentation    |
+-------------+                                +-------------------+                       +--------------------+
```

### Core Tools Evaluated
- `resolve-library-id`: Maps human-readable package or library names (e.g., `"fastapi"`, `"mcp-sdk"`) to standardized library identifiers.
- `query-docs`: Retrieves concise, relevant documentation snippets, function signatures, and code examples for a given library ID and topic query.

### Real-World Utility & Experience
- **Eliminating Hallucinations**: When writing code for fast-moving frameworks (such as MCP SDK v2.0 or modern Pydantic v2), the LLM queries Context7 instead of guessing deprecated APIs.
- **Token Efficiency**: Instead of scraping massive web pages and overwhelming context windows, Context7 returns curated markdown snippets focused precisely on the requested symbol.
- **Latency & Reliability**: Because queries run over stdio JSON-RPC, the client experiences near-instant responses with structured error reporting if a symbol is missing.

---

## 3. Deep Dive: Playwright / Chrome DevTools MCP

### What Does Playwright / Chrome DevTools MCP Do?
Traditional LLMs cannot execute client-side code, interact with single-page applications (SPAs), or observe visual layouts. **Playwright / Chrome DevTools MCP** connects LLMs directly to a headless or headed browser instance via the Chrome DevTools Protocol (CDP).

```
+-------------+      MCP JSON-RPC (stdio)      +-------------------+      CDP WebSocket    +--------------------+
|  MCP Client | <============================> |   Playwright/CDP  | <===================> |   Chromium Browser |
| (LLM Agent) |    tools/call "take_snapshot"  |     MCP Server    |                       | (DOM / JS Engine)  |
+-------------+                                +-------------------+                       +--------------------+
```

### Core Tools Evaluated
- `navigate_page`: Directs the browser tab to a specified URL.
- `take_snapshot` / `take_screenshot`: Captures the accessibility tree or visual image of the current page.
- `click`, `type_text`, `fill`: Automates user interactions with input fields, buttons, and dropdowns.
- `evaluate_script`: Runs arbitrary JavaScript within the active page context to inspect runtime state.
- `list_console_messages`: Inspects runtime errors and warnings directly from the browser console.

### Real-World Utility & Experience
- **Autonomous QA & Debugging**: The agent can navigate to a local or remote web app, fill out forms, trigger clicks, and inspect console logs without human intervention.
- **Multi-Modal Verification**: When inspecting UI styling and responsiveness, screenshot tools provide image data back to vision-capable models to verify correct visual rendering.
- **Resilient Error Recovery**: When a selector is missing, the server returns informative errors, allowing the LLM to inspect the DOM tree and self-correct with an updated selector.

---

## 4. Key Takeaways Applied to QuickMemo MCP

Evaluating Context7 and Playwright MCP revealed the essential traits of high-quality MCP servers:

1. **Clear, Semantic Tool Signatures**: Tool names and docstrings serve as the LLM's API documentation. They must explicitly describe what the tool does, expected parameter formats, and realistic examples.
2. **Minimalist, Focused Scope**: The most useful MCP servers do one thing exceptionally well. Avoiding unnecessary dependencies and bloated abstractions makes servers faster and easier to deploy.
3. **Structured Outputs**: Returning predictable, formatted markdown or JSON allows LLMs to parse and present information cleanly to end users.
4. **All Three Primitives (Tools, Resources, Prompts)**: While many servers only provide Tools, implementing **Resources** (for dynamic context reading) and **Prompts** (for reusable workflow templates) creates a complete, professional MCP experience.

These principles directly shaped the design and architecture of **QuickMemo MCP**.
