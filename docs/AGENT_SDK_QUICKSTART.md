# Claude Agent SDK Quickstart

> Build programmatic AI agents with Claude Code's capabilities.

## What is the Claude Agent SDK?

The Claude Agent SDK provides programmatic access to Claude Code's full capabilities:

- **Built-in Tools**: File operations, shell commands, search—no implementation needed
- **Session Management**: Resume, fork, and maintain context across interactions
- **MCP Integration**: Connect to external systems (browsers, databases, APIs)
- **Hook System**: Customize behavior at runtime

The SDK is available in both **Python** and **TypeScript**.

---

## Installation

### Prerequisites

1. **Claude Code CLI** (runtime):
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. **API Key**: Set `ANTHROPIC_API_KEY` in your environment

### Python SDK

```bash
pip install claude-code-sdk
```

### TypeScript SDK

```bash
npm install @anthropic-ai/claude-code-sdk
```

---

## Your First Agent

### Python

```python
import asyncio
from claude_code_sdk import query, ClaudeCodeOptions

async def main():
    async for message in query(
        prompt="List all Python files in the current directory",
        options=ClaudeCodeOptions(
            allowed_tools=["Glob", "Read"]
        )
    ):
        if hasattr(message, 'content'):
            print(message.content)

asyncio.run(main())
```

### TypeScript

```typescript
import { query, ClaudeCodeOptions } from '@anthropic-ai/claude-code-sdk';

async function main() {
  for await (const message of query({
    prompt: "List all Python files in the current directory",
    options: {
      allowedTools: ["Glob", "Read"]
    }
  })) {
    if ('content' in message) {
      console.log(message.content);
    }
  }
}

main();
```

---

## Built-in Tools

The SDK includes these tools with no additional setup:

| Tool | Purpose | Example Use |
|------|---------|-------------|
| **Read** | Read file contents | `Read("src/main.py")` |
| **Write** | Create new files | `Write("output.txt", content)` |
| **Edit** | Modify existing files | `Edit("config.json", old, new)` |
| **Bash** | Execute shell commands | `Bash("npm test")` |
| **Glob** | Find files by pattern | `Glob("**/*.ts")` |
| **Grep** | Search file contents | `Grep("TODO", "src/")` |
| **Task** | Spawn sub-agents | Automatic delegation |
| **WebFetch** | Fetch web content | `WebFetch("https://...")` |
| **WebSearch** | Search the web | `WebSearch("Claude SDK docs")` |

### Tool Permissions

Control which tools the agent can use:

```python
# Allow specific tools
options = ClaudeCodeOptions(
    allowed_tools=["Read", "Glob", "Grep"]  # Read-only
)

# Allow all tools (use with caution)
options = ClaudeCodeOptions(
    bypass_permissions=True
)

# Auto-accept file edits
options = ClaudeCodeOptions(
    accept_edits=True
)
```

---

## Session Management

### Capturing Session ID

```python
session_id = None

async for message in query(prompt="Analyze the codebase structure"):
    if message.type == "system" and message.subtype == "init":
        session_id = message.session_id
        print(f"Session started: {session_id}")

    if hasattr(message, 'content'):
        print(message.content)
```

### Resuming Sessions

Continue a previous conversation with full context:

```python
# Later, resume the session
async for message in query(
    prompt="Now refactor the auth module based on your analysis",
    options=ClaudeCodeOptions(resume=session_id)
):
    print(message.content)
```

### Forking Sessions

Create a branch for exploration without affecting the original:

```python
async for message in query(
    prompt="Try an alternative approach",
    options=ClaudeCodeOptions(
        resume=session_id,
        fork=True  # Creates a new branch
    )
):
    print(message.content)
```

---

## Hooks

Customize agent behavior at runtime:

### PreToolUse Hook

Validate or modify tool calls before execution:

```python
def validate_bash(tool_name: str, params: dict) -> bool:
    """Block dangerous commands."""
    if tool_name == "Bash":
        cmd = params.get("command", "")
        if "rm -rf" in cmd or "sudo" in cmd:
            return False
    return True

options = ClaudeCodeOptions(
    hooks={
        "PreToolUse": validate_bash
    }
)
```

### PostToolUse Hook

Process results after tool execution:

```python
def log_tool_use(tool_name: str, result: dict) -> dict:
    """Log all tool usage."""
    print(f"Tool: {tool_name}")
    print(f"Result: {result}")
    return result  # Return unchanged or modified

options = ClaudeCodeOptions(
    hooks={
        "PostToolUse": log_tool_use
    }
)
```

### Available Hooks

| Hook | Timing | Use Case |
|------|--------|----------|
| `PreToolUse` | Before tool runs | Validation, blocking |
| `PostToolUse` | After tool runs | Logging, transformation |
| `SessionStart` | Session begins | Setup, initialization |
| `SessionEnd` | Session ends | Cleanup, reporting |
| `Stop` | Agent stops | Final processing |

---

## MCP Integration

Connect to external systems via Model Context Protocol:

### Browser Automation (Playwright)

```python
options = ClaudeCodeOptions(
    mcp_servers={
        "playwright": {
            "command": "npx",
            "args": ["@anthropic-ai/mcp-server-playwright"]
        }
    }
)

async for message in query(
    prompt="Navigate to example.com and screenshot the homepage",
    options=options
):
    print(message.content)
```

### Database Access (PostgreSQL)

```python
options = ClaudeCodeOptions(
    mcp_servers={
        "postgres": {
            "command": "npx",
            "args": ["@anthropic-ai/mcp-server-postgres"],
            "env": {
                "DATABASE_URL": "postgresql://user:pass@localhost/db"
            }
        }
    }
)
```

### Custom MCP Server

```python
options = ClaudeCodeOptions(
    mcp_servers={
        "custom": {
            "command": "python",
            "args": ["my_mcp_server.py"],
            "cwd": "/path/to/server"
        }
    }
)
```

---

## Message Types

The SDK streams various message types:

```python
async for message in query(prompt="..."):
    match message.type:
        case "system":
            # Session management (init, stop, etc.)
            if message.subtype == "init":
                print(f"Started: {message.session_id}")

        case "assistant":
            # Claude's responses
            print(message.content)

        case "tool_use":
            # Tool being called
            print(f"Using: {message.tool_name}")

        case "tool_result":
            # Tool output
            print(f"Result: {message.result}")

        case "error":
            # Error occurred
            print(f"Error: {message.error}")
```

---

## Error Handling

### Graceful Error Recovery

```python
from claude_code_sdk import query, ClaudeCodeOptions, SDKError

async def safe_query(prompt: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            async for message in query(prompt=prompt):
                yield message
            return
        except SDKError as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### Timeout Configuration

```python
options = ClaudeCodeOptions(
    timeout=300,  # 5 minutes max
    max_tokens=4096
)
```

---

## Complete Example: Code Review Agent

```python
import asyncio
from claude_code_sdk import query, ClaudeCodeOptions

async def review_pr(pr_number: int):
    """Review a pull request and provide feedback."""

    session_id = None

    # Phase 1: Analyze changes
    print("Analyzing PR...")
    async for msg in query(
        prompt=f"Analyze the changes in PR #{pr_number}. List all modified files and summarize the changes.",
        options=ClaudeCodeOptions(
            allowed_tools=["Bash", "Read", "Glob", "Grep"]
        )
    ):
        if msg.type == "system" and msg.subtype == "init":
            session_id = msg.session_id
        if hasattr(msg, 'content'):
            print(msg.content)

    # Phase 2: Review code quality
    print("\nReviewing code quality...")
    async for msg in query(
        prompt="Review the code for: 1) bugs, 2) security issues, 3) performance problems, 4) style violations",
        options=ClaudeCodeOptions(resume=session_id)
    ):
        if hasattr(msg, 'content'):
            print(msg.content)

    # Phase 3: Generate summary
    print("\nGenerating review summary...")
    async for msg in query(
        prompt="Provide a final review summary with a recommendation (approve/request changes)",
        options=ClaudeCodeOptions(resume=session_id)
    ):
        if hasattr(msg, 'content'):
            print(msg.content)

if __name__ == "__main__":
    asyncio.run(review_pr(123))
```

---

## Best Practices

### 1. Least Privilege

Only grant tools the agent actually needs:

```python
# Good: Minimal permissions
options = ClaudeCodeOptions(
    allowed_tools=["Read", "Glob"]  # Read-only
)

# Bad: Overly permissive
options = ClaudeCodeOptions(
    bypass_permissions=True  # Only for trusted scenarios
)
```

### 2. Session Reuse

Reuse sessions to maintain context and reduce costs:

```python
# First interaction
session_id = await analyze_code()

# Follow-up (uses existing context)
await fix_issues(session_id)
```

### 3. Structured Output

Request structured output for programmatic use:

```python
async for msg in query(
    prompt="List issues as JSON array: [{file, line, issue, severity}]",
    options=options
):
    if hasattr(msg, 'content'):
        issues = json.loads(msg.content)
```

### 4. Progress Tracking

For long tasks, track progress:

```python
async def run_with_progress(prompt: str):
    tool_count = 0

    async for msg in query(prompt=prompt):
        if msg.type == "tool_use":
            tool_count += 1
            print(f"Step {tool_count}: {msg.tool_name}")

        yield msg
```

---

## Configuration Reference

### ClaudeCodeOptions

| Option | Type | Description |
|--------|------|-------------|
| `allowed_tools` | `list[str]` | Tools the agent can use |
| `bypass_permissions` | `bool` | Allow all operations |
| `accept_edits` | `bool` | Auto-accept file changes |
| `resume` | `str` | Session ID to resume |
| `fork` | `bool` | Fork instead of resume |
| `timeout` | `int` | Max execution time (seconds) |
| `max_tokens` | `int` | Max response tokens |
| `mcp_servers` | `dict` | MCP server configuration |
| `hooks` | `dict` | Runtime hooks |
| `cwd` | `str` | Working directory |
| `env` | `dict` | Environment variables |

---

## Resources

- [Claude Agent SDK Documentation](https://docs.anthropic.com/en/docs/claude-code/sdk)
- [MCP Server Examples](https://github.com/anthropics/mcp-servers)
- [Autonomous Coding Quickstart](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)
- [Agentic Patterns Guide](AGENTIC_GUIDE.md)
