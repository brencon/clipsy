# Agent Examples

Working examples demonstrating agentic patterns with Claude Code.

## Examples

### autonomous-task/

A long-running agent implementation based on [Anthropic's two-agent pattern](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).

**Features**:
- Two-agent architecture (initializer + worker)
- File-based state management
- Security-first command validation
- Pausable/resumable execution
- Git-based checkpointing

## Quick Start

### Prerequisites

1. **Claude Code CLI** installed:
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. **Python 3.10+** with dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **API Key** set:
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   ```

### Running the Autonomous Task Example

```bash
cd autonomous-task

# First run - initializes the task
python main.py --task "Implement a REST API for user management"

# Subsequent runs - continues from saved state
python main.py

# Check progress
cat progress.txt

# View task status
cat feature_list.json
```

## How It Works

### Two-Agent Pattern

```
┌─────────────────────────────────────────────────────┐
│                    First Run                         │
│  ┌─────────────────────────────────────────────┐    │
│  │           Initializer Agent                  │    │
│  │  • Analyzes requirements                     │    │
│  │  • Creates feature_list.json                 │    │
│  │  • Sets up progress.txt                      │    │
│  │  • Makes initial progress                    │    │
│  └─────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                 Subsequent Runs                      │
│  ┌─────────────────────────────────────────────┐    │
│  │             Worker Agent                     │    │
│  │  1. Read progress.txt & feature_list.json    │    │
│  │  2. Run tests to verify state                │    │
│  │  3. Fix any undocumented bugs                │    │
│  │  4. Continue with next feature               │    │
│  │  5. Commit checkpoint                        │    │
│  └─────────────────────────────────────────────┘    │
│                         │                            │
│                         ▼                            │
│              ┌─────────────────┐                    │
│              │  More features? │                    │
│              └────────┬────────┘                    │
│                  YES  │  NO                          │
│                  ┌────┴────┐                        │
│                  ▼         ▼                        │
│              [Loop]    [Done]                       │
└─────────────────────────────────────────────────────┘
```

### State Files

| File | Purpose |
|------|---------|
| `progress.txt` | Human-readable log of completed work |
| `feature_list.json` | Structured task tracking with status |
| Git commits | Checkpoints for rollback |

### Security Model

Commands are validated against an allowlist:

```python
ALLOWED_COMMANDS = [
    "ls", "cat", "head", "tail", "wc", "grep", "find",
    "npm", "node", "python", "pip", "pytest",
    "git", "make", "echo", "date", "pwd"
]
```

Dangerous patterns are blocked:
- `rm -rf` - Recursive deletion
- `sudo` - Privilege escalation
- `curl | sh` - Remote code execution

## Customization

### Adding Allowed Commands

Edit `autonomous-task/security.py`:

```python
ALLOWED_COMMANDS = [
    # ... existing commands ...
    "docker",  # Add Docker support
    "kubectl", # Add Kubernetes support
]
```

### Changing the Agent Prompts

Modify the prompts in `autonomous-task/prompts/`:
- `initializer.md` - First session behavior
- `worker.md` - Continuation sessions

### Adjusting State Management

Edit `autonomous-task/progress.py` to customize:
- Progress file format
- Feature list structure
- Completion criteria

## Learn More

- [Agentic Patterns Guide](../../docs/AGENTIC_GUIDE.md)
- [Agent SDK Quickstart](../../docs/AGENT_SDK_QUICKSTART.md)
- [Anthropic's Research](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
