# Building Agentic Solutions with Claude

> A comprehensive guide to building AI systems that autonomously complete complex tasks.

## What is an Agentic Solution?

An **agentic solution** is an AI system that autonomously takes actions to achieve goals. Unlike simple chat interactions, agents:

- **Plan**: Break complex tasks into steps
- **Execute**: Use tools to make changes
- **Observe**: Check results and adapt
- **Persist**: Maintain state across sessions

Claude Code provides a powerful foundation for building agentic solutions through its combination of instructions (CLAUDE.md), tools, and an agentic loop.

### When to Use Agents vs. Simple Chat

| Scenario | Approach |
|----------|----------|
| Quick question about code | Simple chat |
| Single file edit | Simple chat |
| Multi-file refactoring | Agent (sub-agent) |
| Long-running implementation | Agent (two-agent pattern) |
| Repeatable workflow | Agent (skill) |
| Important decision | Agent (LLM Council) |

---

## Agentic Patterns in Claude Code

This template supports four agentic patterns, each suited to different use cases:

### Pattern 1: Sub-Agents (Task-Based Delegation)

**When to use**: Complex tasks that benefit from isolated context and parallel execution.

**How it works**: Claude Code automatically spawns sub-agents using the Task tool when:
- A subtask is complex enough to warrant delegation
- Parallel execution would be more efficient
- Isolated context helps focus

**Best for**:
- Code exploration and analysis
- Documentation generation
- Research tasks
- File transformations

**Example workflow**:
```
User: "Review this PR for security issues"

Claude spawns sub-agents for:
├── Agent 1: Check authentication code
├── Agent 2: Review SQL queries
├── Agent 3: Analyze input validation
└── Main: Synthesize findings
```

**Configuration**: Sub-agents are enabled by default. No additional setup required.

---

### Pattern 2: Skills (Automated Workflows)

**When to use**: Repeatable, specialized tasks that should execute consistently.

**How it works**: Define workflows in `.claude/skills/SKILL_NAME.md` that Claude follows for specific tasks.

**Best for**:
- "Digital employee" automation
- Deterministic workflows
- Task standardization
- Role-specific behavior

**Example skill** (`.claude/skills/deploy-preview.md`):
```markdown
# Deploy Preview Skill

## Trigger
User requests a preview deployment

## Steps
1. Run tests: `npm test`
2. Build: `npm run build`
3. Deploy: `npx vercel --preview`
4. Return preview URL
```

**Documentation**: See `docs/SKILLS_GUIDE.md` for detailed skill development.

---

### Pattern 3: LLM Council (Multi-Model Decisions)

**When to use**: Important decisions that benefit from diverse AI perspectives.

**How it works**: Consult multiple AI models (Claude, GPT-4, Gemini, Grok) through a three-stage process:
1. Gather independent responses
2. Peer review and ranking
3. Chairman synthesis

**Best for**:
- Architecture decisions
- Technology choices
- Plan evaluation
- Tie-breaking between valid approaches

**Usage**:
```
/council Should we use PostgreSQL or MongoDB for this use case?
```

**Documentation**: See `docs/LLM_COUNCIL_GUIDE.md` for setup and configuration.

---

### Pattern 4: Long-Running Agents (Two-Agent Pattern)

**When to use**: Tasks spanning hours or days that require multiple sessions.

**How it works**: Based on [Anthropic's research](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), this pattern uses two specialized agents:

1. **Initializer Agent** (First session):
   - Analyzes requirements
   - Creates structured feature list
   - Sets up state tracking files
   - Makes initial progress

2. **Coding Agent** (Subsequent sessions):
   - Reads previous progress
   - Runs tests to check state
   - Fixes any undocumented bugs
   - Continues implementation
   - Commits checkpoints

**State files**:
```
project/
├── claude-progress.txt    # Human-readable status log
├── feature_list.json      # Structured task tracking
└── .git/                  # Checkpoints via commits
```

**Example**: See `scripts/agent-examples/` for a working implementation.

---

## State Management

Effective state management is critical for agentic solutions. Claude Code supports several patterns:

### File-Based State (Recommended)

The most robust approach uses files to persist state:

#### progress.txt
Human-readable log of what's been done:
```
# Progress Log

## 2025-01-15 14:30
- Analyzed authentication requirements
- Implemented JWT token generation
- Added unit tests for auth module

## 2025-01-15 16:45
- Started password reset flow
- Created email template
- TODO: Wire up SMTP configuration
```

#### feature_list.json
Structured task tracking:
```json
{
  "features": [
    {
      "id": "auth-jwt",
      "name": "JWT Authentication",
      "status": "complete",
      "files": ["src/auth/jwt.ts", "tests/auth.test.ts"]
    },
    {
      "id": "auth-reset",
      "name": "Password Reset",
      "status": "in_progress",
      "files": ["src/auth/reset.ts"],
      "blockers": ["Need SMTP config"]
    }
  ]
}
```

#### Git Commits
Use incremental commits as checkpoints:
```bash
# After each feature
git add -A
git commit -m "feat(auth): implement JWT token generation"
```

### Session Continuity

For interactive agents, use session IDs:

```python
from claude_code_sdk import query, ClaudeCodeOptions

# Initial session
async for msg in query(prompt="Analyze the auth module"):
    if msg.type == "system" and msg.subtype == "init":
        session_id = msg.session_id

# Resume later
async for msg in query(
    prompt="Now implement the fixes",
    options=ClaudeCodeOptions(resume=session_id)
):
    print(msg)
```

### Context Window Management

For long tasks, manage context proactively:
- Summarize progress periodically
- Commit and reference git history
- Use file-based state over memory
- Archive completed work to separate files

---

## Security Patterns

### Defense in Depth

Layer security controls for production agents:

```
┌─────────────────────────────────────┐
│  1. OS-Level Sandbox                │
│  ┌─────────────────────────────────┐│
│  │  2. Filesystem Restrictions     ││
│  │  ┌─────────────────────────────┐││
│  │  │  3. Command Allowlist       │││
│  │  │  ┌─────────────────────────┐│││
│  │  │  │  4. Hook Validation     ││││
│  │  │  │         Agent           ││││
│  │  │  └─────────────────────────┘│││
│  │  └─────────────────────────────┘││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
```

### Command Allowlist (Recommended)

Use allowlists, not blocklists:

```python
# security.py
ALLOWED_COMMANDS = [
    # File operations (read-only)
    "ls", "cat", "head", "tail", "wc", "find",

    # Development tools
    "npm", "node", "python", "pip",
    "git", "make",

    # Testing
    "pytest", "jest", "npm test",

    # Safe utilities
    "echo", "date", "pwd", "which"
]

BLOCKED_PATTERNS = [
    r"rm\s+-rf",           # Recursive delete
    r">\s*/dev/",          # Device writes
    r"curl.*\|.*sh",       # Pipe to shell
    r"sudo",               # Privilege escalation
]

def validate_command(cmd: str) -> bool:
    """Check if command is allowed."""
    base_cmd = cmd.split()[0]

    # Check blocklist first
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, cmd):
            return False

    # Then verify allowlist
    return base_cmd in ALLOWED_COMMANDS
```

### Hook-Based Validation

Use Claude Code hooks for runtime validation:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python scripts/validate_command.py \"$CLAUDE_COMMAND\""
          }
        ]
      }
    ]
  }
}
```

### Filesystem Restrictions

Limit agent access to specific directories:

```python
ALLOWED_PATHS = [
    "/project/src",
    "/project/tests",
    "/project/docs"
]

FORBIDDEN_PATHS = [
    "/etc",
    "/usr",
    "~/.ssh",
    "~/.aws"
]
```

---

## Error Handling & Resilience

### Session Startup Protocol

Every session should start with validation:

```markdown
## Session Startup Checklist

1. **Read State**
   - Load progress.txt
   - Parse feature_list.json
   - Check last git commit

2. **Run Tests**
   - Execute test suite
   - Note any failures

3. **Fix Undocumented Issues**
   - If tests fail unexpectedly, fix first
   - Update progress tracking

4. **Continue Work**
   - Pick up from last tracked item
   - Make incremental progress
```

### Recovery Strategies

| Failure | Recovery |
|---------|----------|
| Test failure | Roll back to last passing commit |
| API timeout | Exponential backoff retry |
| Context overflow | Summarize and continue |
| Invalid state | Reset from feature_list.json |

### Retry Pattern

```python
import asyncio
from typing import TypeVar, Callable

T = TypeVar('T')

async def with_retry(
    fn: Callable[[], T],
    max_attempts: int = 3,
    base_delay: float = 1.0
) -> T:
    """Execute with exponential backoff."""
    for attempt in range(max_attempts):
        try:
            return await fn()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            delay = base_delay * (2 ** attempt)
            await asyncio.sleep(delay)
```

---

## Testing Agentic Solutions

### Unit Testing

Test individual components in isolation:

```python
# test_progress.py
import pytest
from progress import ProgressTracker

def test_load_empty_progress():
    tracker = ProgressTracker("nonexistent.txt")
    assert tracker.entries == []

def test_add_entry():
    tracker = ProgressTracker()
    tracker.add("Completed auth module")
    assert len(tracker.entries) == 1
    assert "auth" in tracker.entries[0].content
```

### Integration Testing

Test complete workflows:

```python
# test_agent_workflow.py
import pytest
from agent import CodingAgent

@pytest.mark.asyncio
async def test_agent_completes_simple_task():
    agent = CodingAgent(
        feature_list="test_features.json",
        sandbox=True
    )

    result = await agent.run("Add a hello world endpoint")

    assert result.status == "complete"
    assert "endpoint" in result.files_modified
```

### Cost Estimation

Estimate costs before running:

```python
def estimate_cost(task: str, mode: str = "standard") -> dict:
    """Estimate token usage and cost."""

    # Rough estimates based on task complexity
    estimates = {
        "simple": {"input": 1000, "output": 500},
        "standard": {"input": 5000, "output": 2000},
        "complex": {"input": 20000, "output": 10000}
    }

    tokens = estimates.get(mode, estimates["standard"])

    # Claude Sonnet pricing (as of 2025)
    cost = (tokens["input"] * 0.003 + tokens["output"] * 0.015) / 1000

    return {
        "estimated_tokens": tokens,
        "estimated_cost_usd": round(cost, 4)
    }
```

---

## Monitoring & Observability

### Logging Pattern

Structure logs for analysis:

```python
import json
import logging
from datetime import datetime

class AgentLogger:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.logger = logging.getLogger(f"agent.{session_id}")

    def log_action(self, action: str, details: dict):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "session": self.session_id,
            "action": action,
            **details
        }
        self.logger.info(json.dumps(entry))
```

### Metrics to Track

| Metric | Purpose |
|--------|---------|
| Session duration | Performance |
| Token usage | Cost control |
| Tool calls | Efficiency |
| Error rate | Reliability |
| Task completion | Success rate |

---

## Best Practices Checklist

### Before Starting

- [ ] Define clear completion criteria
- [ ] Choose appropriate agent pattern
- [ ] Set up state management files
- [ ] Configure security allowlists
- [ ] Estimate cost and time

### During Development

- [ ] Implement progress tracking
- [ ] Use git for checkpointing
- [ ] Test before continuing work
- [ ] Handle errors gracefully
- [ ] Log important decisions

### For Production

- [ ] Layer security controls
- [ ] Set up monitoring
- [ ] Plan for session interruption
- [ ] Document recovery procedures
- [ ] Test failure scenarios

---

## Architecture Decision Guide

### Choosing the Right Pattern

```
┌─────────────────────────────────────────────────────┐
│                   What's the task?                   │
└─────────────────────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
    ┌─────────┐    ┌──────────┐   ┌──────────┐
    │ Single  │    │ Multiple │   │ Decision │
    │ Complex │    │ Sessions │   │ Needed   │
    │  Task   │    │ Required │   │          │
    └────┬────┘    └────┬─────┘   └────┬─────┘
         │              │              │
         ▼              ▼              ▼
   ┌───────────┐  ┌───────────┐  ┌───────────┐
   │ Sub-Agent │  │ Two-Agent │  │   LLM     │
   │  Pattern  │  │  Pattern  │  │  Council  │
   └───────────┘  └───────────┘  └───────────┘
         │              │              │
         │              │              │
         ▼              ▼              ▼
    ┌─────────┐    ┌──────────┐   ┌──────────┐
    │Repeatable│   │ Use SDK  │   │ Configure│
    │workflow? │   │   for    │   │  models  │
    │    │     │   │production│   │ & modes  │
    └────┼────┘    └──────────┘   └──────────┘
         │
    YES  │  NO
    ┌────┴────┐
    ▼         ▼
┌───────┐  ┌───────┐
│ Skill │  │ Done  │
└───────┘  └───────┘
```

---

## Resources

### Anthropic Resources
- [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Claude Agent SDK Documentation](https://docs.anthropic.com/en/docs/claude-code/sdk)
- [Autonomous Coding Quickstart](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)

### Template Resources
- [Agent SDK Quickstart](AGENT_SDK_QUICKSTART.md) - Getting started with programmatic agents
- [Skills Guide](SKILLS_GUIDE.md) - Building automated workflows
- [LLM Council Guide](LLM_COUNCIL_GUIDE.md) - Multi-model decision making
- [Best Practices](BEST_PRACTICES.md) - General Claude Code patterns

### Example Code
- `scripts/agent-examples/` - Working agent implementations
- `examples/agentic-claude-md/` - CLAUDE.md optimized for agents
