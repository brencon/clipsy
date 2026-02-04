# Project Instructions for Claude Code (Agentic Template)

> Optimized CLAUDE.md template for building agentic AI solutions.
> Use this when your project will involve long-running agents, automated workflows, or programmatic Claude integration.

## Project Overview

[PROJECT_NAME] is an agentic AI solution that [BRIEF_DESCRIPTION].

**Agent Type**: [Sub-Agent | Skill | Long-Running | SDK Integration]

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   [Your Agent]                       │
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │    State    │  │   Tools     │  │  Security   │ │
│  │  Management │  │ Integration │  │  Validation │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────┤
│                 Claude Code / SDK                    │
└─────────────────────────────────────────────────────┘
```

## Directory Structure

```
├── .claude/
│   ├── commands/         # Custom slash commands
│   ├── skills/           # Automated workflows (if using skills pattern)
│   └── settings.json     # Permission configuration
├── src/
│   ├── agent/            # Agent implementation
│   │   ├── main.py       # Entry point
│   │   ├── state.py      # State management
│   │   └── security.py   # Command validation
│   └── ...
├── prompts/              # Agent prompt templates
├── state/                # Runtime state files (gitignored)
│   ├── progress.txt
│   └── feature_list.json
├── tests/
└── CLAUDE.md
```

## State Management

### State Files

| File | Purpose | Persistence |
|------|---------|-------------|
| `state/progress.txt` | Human-readable progress log | Gitignored |
| `state/feature_list.json` | Structured task tracking | Gitignored |
| Git commits | Checkpoints | Permanent |

### Session Startup Protocol

Every session MUST start with:

1. **Read State**
   ```bash
   cat state/progress.txt
   cat state/feature_list.json
   ```

2. **Run Tests**
   ```bash
   [TEST_COMMAND]
   ```

3. **Fix Undocumented Bugs**
   - If tests fail, fix before continuing
   - Update progress.txt with fixes

4. **Continue Work**
   - Pick up from last tracked feature
   - Make incremental progress

### Checkpointing

After completing each feature:
```bash
git add -A
git commit -m "feat(agent): [feature name]"
```

## Security Configuration

### Command Allowlist

Only these commands are permitted:

```python
ALLOWED_COMMANDS = [
    # Read operations
    "ls", "cat", "head", "tail", "find", "grep",

    # Development
    [ADD_YOUR_ALLOWED_COMMANDS],

    # Version control
    "git",
]
```

### Blocked Patterns

These patterns are ALWAYS blocked:
- `rm -rf` - Recursive deletion
- `sudo` - Privilege escalation
- `curl | sh` - Remote execution
- `git push --force` - History destruction

### Filesystem Scope

```python
ALLOWED_PATHS = [
    "src/",
    "tests/",
    "docs/",
    "state/",
]

FORBIDDEN_PATHS = [
    ".env",
    ".git/config",
    "~/.ssh/",
]
```

## Agent Behavior

### Core Loop

```
┌─────────────────────────────────────────┐
│           Agent Main Loop               │
├─────────────────────────────────────────┤
│  1. Load state from files               │
│  2. Run tests to verify state           │
│  3. Fix any failures                    │
│  4. Get next pending feature            │
│  5. Implement feature                   │
│  6. Write/update tests                  │
│  7. Verify tests pass                   │
│  8. Commit checkpoint                   │
│  9. Update state files                  │
│  10. Loop or exit                       │
└─────────────────────────────────────────┘
```

### Error Handling

| Error Type | Recovery Action |
|------------|-----------------|
| Test failure | Roll back to last commit, analyze |
| API timeout | Exponential backoff retry |
| Invalid state | Reset from feature_list.json |
| Blocked feature | Skip, log, continue with next |

### Completion Criteria

The agent considers work complete when:
- [ ] All features in feature_list.json are "complete"
- [ ] All tests pass
- [ ] All changes committed
- [ ] progress.txt updated with final summary

## Development Commands

### Build & Run

```bash
# Run the agent (first time)
python src/agent/main.py --task "Your task description"

# Run the agent (continue)
python src/agent/main.py

# Check progress
cat state/progress.txt

# View feature status
cat state/feature_list.json | python -m json.tool
```

### Testing

```bash
# Run all tests
[TEST_COMMAND]

# Run agent tests specifically
[AGENT_TEST_COMMAND]
```

## Integration Points

### MCP Servers (if applicable)

```yaml
mcp_servers:
  # Browser automation
  playwright:
    command: npx
    args: ["@anthropic-ai/mcp-server-playwright"]

  # Database access
  # postgres:
  #   command: npx
  #   args: ["@anthropic-ai/mcp-server-postgres"]
```

### External APIs

| Service | Purpose | Auth |
|---------|---------|------|
| [SERVICE] | [PURPOSE] | [AUTH_METHOD] |

## Rules for Claude

### Agentic Principles

1. **State is truth**: Always read state files before acting
2. **Test constantly**: Run tests before and after every change
3. **Checkpoint frequently**: Commit after each logical unit of work
4. **Log everything**: Update progress.txt with what you're doing
5. **Fail safely**: If something goes wrong, roll back and document

### Before Each Session

1. Read progress.txt to understand where we left off
2. Read feature_list.json to know what's pending
3. Run the test suite to verify state
4. Fix any failures before continuing

### During Implementation

- Follow existing code patterns
- Write tests for new functionality
- Keep changes focused and atomic
- Update state files as you go

### Before Ending Session

1. Run full test suite
2. Commit all changes
3. Update progress.txt with session summary
4. Ensure feature_list.json is accurate

### When Blocked

1. Update feature status to "blocked"
2. Document the blocker clearly
3. Move to the next feature
4. Note in progress.txt

## Troubleshooting

### Agent Seems Stuck

```bash
# Check current state
cat state/progress.txt | tail -20
cat state/feature_list.json

# Check for uncommitted changes
git status

# Check test status
[TEST_COMMAND]
```

### Tests Failing Unexpectedly

1. Check if this is from a previous session
2. Review progress.txt for context
3. Fix before continuing new work
4. Document the fix

### State Files Missing

```bash
# Re-initialize
python src/agent/main.py --task "Your task" --force
```

---

## Quick Reference

| Action | Command/Location |
|--------|------------------|
| Start new task | `python src/agent/main.py --task "..."` |
| Continue task | `python src/agent/main.py` |
| Check progress | `cat state/progress.txt` |
| View features | `cat state/feature_list.json` |
| Run tests | `[TEST_COMMAND]` |
| Manual checkpoint | `git add -A && git commit -m "checkpoint"` |

---

*This template is optimized for agentic AI solutions. See `docs/AGENTIC_GUIDE.md` for detailed patterns and best practices.*
