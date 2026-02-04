# Health Check

Run a diagnostic check to verify Claude Code setup and configuration.

## Instructions

Perform a comprehensive health check of the project setup:

### 1. Core Structure Check

Verify these essential files exist:
- `CLAUDE.md` - Project instructions
- `.claude/settings.json` - Claude Code settings
- `.claude/commands/` - Slash commands directory

### 2. Git Status

Check if the project is a git repository and show current status:
```bash
git status --short
```

### 3. Environment Check

Check if `.env` file exists (without revealing contents):
- If `.env` exists: Report "Environment file configured"
- If missing: Suggest copying from `.env.example`

### 4. LLM Council Status (Optional)

Check council configuration:
- Does `scripts/llm-council/config.yaml` exist?
- Are Python dependencies installed? (`pip show pyyaml httpx python-dotenv`)
- Report which providers appear to be configured (check for non-empty API key variables in .env, don't show the actual keys)

### 5. Slash Commands Inventory

List all available slash commands in `.claude/commands/`:
```bash
ls -1 .claude/commands/*.md
```

### 6. Documentation Check

Verify key documentation files exist:
- `README.md`
- `docs/GETTING_STARTED.md`
- `docs/BEST_PRACTICES.md`

## Output Format

Present results as a clear status report:

```
=== Claude Code Health Check ===

Core Structure:     [OK/MISSING items]
Git Repository:     [OK/NOT INITIALIZED]
Environment:        [CONFIGURED/NEEDS SETUP]
LLM Council:        [READY/NEEDS SETUP/NOT CONFIGURED]
Slash Commands:     [X commands available]
Documentation:      [OK/MISSING items]

[Any recommendations or next steps]
```

## When Issues Found

If any checks fail, provide specific remediation steps:
- Missing files: Show how to create them
- Missing dependencies: Show install commands
- Configuration issues: Point to relevant documentation
