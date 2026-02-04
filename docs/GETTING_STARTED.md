# Getting Started with Claude Code Project Template

> A step-by-step guide to using this template for your projects.

## Table of Contents

- [Choosing Your Approach](#choosing-your-approach)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Customization Checklist](#customization-checklist)
- [Syncing Upstream Updates](#syncing-upstream-updates)
- [First Claude Code Session](#first-claude-code-session)
- [Troubleshooting](#troubleshooting)

---

## Choosing Your Approach

There are three ways to use this template, each with different tradeoffs:

### Option 1: GitHub Template (Recommended for Most Users)

**Best for:** Starting fresh projects where you want a clean git history.

**Pros:**
- Clean commit history (starts fresh)
- Simple one-click setup on GitHub
- No upstream remote to manage
- Full ownership of your repository

**Cons:**
- Manual effort to sync template updates
- No automatic connection to upstream

**How it works:** GitHub creates a new repository with the template's files but without its git history.

### Option 2: Fork

**Best for:** When you want to contribute back to the template or easily pull updates.

**Pros:**
- Easy to sync upstream changes with `git fetch upstream`
- Can contribute improvements back via PR
- Maintains connection to original template

**Cons:**
- Inherits full commit history
- Fork relationship visible on GitHub
- May have merge conflicts when syncing

**How it works:** Creates a linked copy that maintains a relationship with the original repository.

### Option 3: Clone and Re-initialize

**Best for:** Maximum control, private repositories, or when you don't want any GitHub relationship.

**Pros:**
- Complete independence
- Works with any git hosting (GitLab, Bitbucket, self-hosted)
- Clean history
- Can still add upstream remote for updates

**Cons:**
- More manual setup steps
- No GitHub template/fork UI benefits

---

## Quick Start

### Using GitHub Template (Option 1)

1. Go to [github.com/brencon/claude-code-project-template](https://github.com/brencon/claude-code-project-template)
2. Click **"Use this template"** → **"Create a new repository"**
3. Name your repository and set visibility
4. Click **"Create repository"**
5. Clone your new repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/your-project.git
   cd your-project
   ```
6. Start Claude Code:
   ```bash
   claude
   ```

### Using Fork (Option 2)

1. Go to [github.com/brencon/claude-code-project-template](https://github.com/brencon/claude-code-project-template)
2. Click **"Fork"**
3. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/claude-code-project-template.git my-project
   cd my-project
   ```
4. (Optional) Rename the remote and add upstream:
   ```bash
   git remote rename origin upstream
   git remote add origin https://github.com/YOUR_USERNAME/my-project.git
   ```
5. Start Claude Code:
   ```bash
   claude
   ```

### Using Clone (Option 3)

```bash
# Clone the template
git clone https://github.com/brencon/claude-code-project-template.git my-project
cd my-project

# Remove original remote and reinitialize
rm -rf .git
git init
git add .
git commit -m "Initial commit from Claude Code project template"

# Add your own remote
git remote add origin https://github.com/YOUR_USERNAME/my-project.git
git push -u origin main

# (Optional) Add template as upstream for future updates
git remote add upstream https://github.com/brencon/claude-code-project-template.git
```

---

## Detailed Setup

### Prerequisites

- **Git** installed and configured
- **Claude Code CLI** installed ([installation guide](https://docs.anthropic.com/claude-code/install))
- **GitHub account** (if using GitHub)
- **Anthropic API key** or Claude subscription

### Step 1: Create Your Repository

Choose one of the approaches above and create your repository.

### Step 2: Customize CLAUDE.md

This is the most important step. Open `CLAUDE.md` and update:

```markdown
## Project Overview
[Describe YOUR project - what it does, who it's for, main features]

## Tech Stack
[List YOUR technologies - language, framework, database, etc.]

## Directory Structure
[Update to reflect YOUR project's structure]

## Development Commands
[Add YOUR build, test, lint, and run commands]

## Code Style
[Document YOUR conventions and preferences]
```

### Step 3: Configure Permissions

Edit `.claude/settings.json` to match your workflow:

```json
{
  "permissions": {
    "allow": [
      "Read(*)",
      "Glob(*)",
      "Grep(*)",
      "Bash(git status:*)",
      "Bash(YOUR_TEST_COMMAND:*)",
      "Bash(YOUR_LINT_COMMAND:*)"
    ]
  }
}
```

### Step 4: Set Up Hooks (Optional)

If you want auto-formatting or type-checking, copy from `settings.example.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [{ "type": "command", "command": "npx prettier --write $CLAUDE_FILE_PATH" }]
      }
    ]
  }
}
```

### Step 5: Review and Customize Commands

Check `.claude/commands/` and modify any commands to fit your workflow:

- `brainstorm.md` - Explore options before coding
- `plan.md` - Create implementation plans
- `debug.md` - Systematic debugging
- `review.md` - Code review checklist
- `test.md` - Test generation
- `refactor.md` - Safe refactoring
- `commit.md` - Commit message creation

### Step 6: Clean Up Template Files

Remove or customize files you don't need:

```bash
# Remove example workflow if not using GitHub Actions
rm .github/workflows/claude-code-review.yaml.example

# Or rename to activate it
mv .github/workflows/claude-code-review.yaml.example .github/workflows/claude-code-review.yaml
```

### Step 7: Commit Your Customizations

```bash
git add .
git commit -m "Customize template for [project name]"
git push
```

---

## Customization Checklist

Use this checklist when setting up a new project:

### Required
- [ ] Update `CLAUDE.md` project overview
- [ ] Add your development commands (build, test, lint, run)
- [ ] Update directory structure documentation
- [ ] Configure `.claude/settings.json` permissions

### Recommended
- [ ] Define code style conventions in `CLAUDE.md`
- [ ] Document architecture in `docs/architecture/`
- [ ] Customize slash commands for your workflow
- [ ] Add project-specific patterns to "Important Patterns" section

### Optional
- [ ] Set up hooks for auto-formatting
- [ ] Configure GitHub Actions for PR review
- [ ] Add MCP servers for your integrations
- [ ] Create custom sub-agents for specialized tasks
- [ ] Install skills (front-end design, etc.)
- [ ] Set up PDF parser for large reference documents

---

## Syncing Upstream Updates

When the template is updated with new best practices, you can pull those changes into your project.

### If You Used GitHub Template (Option 1)

Since there's no upstream relationship, you'll need to add one:

```bash
# Add template as upstream (one-time setup)
git remote add upstream https://github.com/brencon/claude-code-project-template.git

# Fetch upstream changes
git fetch upstream

# See what changed
git log upstream/main --oneline -10

# Merge specific files you want (recommended)
git checkout upstream/main -- docs/BEST_PRACTICES.md
git checkout upstream/main -- .claude/commands/new-command.md

# Or merge everything (may have conflicts)
git merge upstream/main --allow-unrelated-histories
```

### If You Forked (Option 2)

```bash
# Fetch upstream changes
git fetch upstream

# Merge upstream changes
git merge upstream/main

# Resolve any conflicts, then
git push origin main
```

### If You Cloned and Added Upstream (Option 3)

Same as GitHub Template approach above.

### Best Practices for Syncing

1. **Don't sync everything blindly** - Review changes first with `git diff`
2. **Sync specific files** - Cherry-pick useful updates:
   ```bash
   # Get just the best practices doc
   git checkout upstream/main -- docs/BEST_PRACTICES.md

   # Get a new slash command
   git checkout upstream/main -- .claude/commands/new-command.md
   ```
3. **Keep your CLAUDE.md** - Don't overwrite your project-specific configuration
4. **Sync periodically** - Check monthly for new patterns and commands

### Watching for Updates

Star and watch the template repository to get notified of updates:

1. Go to [github.com/brencon/claude-code-project-template](https://github.com/brencon/claude-code-project-template)
2. Click **"Watch"** → **"Releases only"** or **"All Activity"**
3. Click **"Star"** to bookmark

---

## First Claude Code Session

After setup, here's how to have a productive first session:

### 1. Verify Setup

```bash
cd your-project
claude
```

Claude will automatically read your `CLAUDE.md`.

### 2. Test the Commands

Try the included slash commands:

```
/brainstorm a user authentication system
```

```
/plan adding a REST API endpoint
```

### 3. Ask Claude to Review

A good first prompt:

```
Review the CLAUDE.md file and suggest any improvements
based on the actual codebase structure.
```

### 4. Start Building

Use the Brainstorm → Plan → Execute workflow:

1. `/brainstorm [your feature idea]`
2. Choose an approach
3. Let Claude plan (Shift+Tab twice for plan mode)
4. Execute the plan

---

## Troubleshooting

### Claude Doesn't See My Files

**Symptoms:** Claude says it can't find files or doesn't know about your project structure.

**Solutions:**
1. Verify you're in the project root: `pwd`
2. Check CLAUDE.md exists: `ls CLAUDE.md`
3. Restart Claude Code: exit and run `claude` again
4. Check if files are gitignored - Claude may skip ignored files
5. Try explicitly mentioning the file path: "Look at src/components/Button.tsx"

### Claude Doesn't See CLAUDE.md

**Symptoms:** Claude doesn't follow your project conventions or commands.

**Solutions:**
- Verify you're in the project root directory
- Check file exists and has correct name (case-sensitive): `ls CLAUDE.md`
- Ensure file isn't empty: `cat CLAUDE.md | head -20`
- Restart Claude Code session

### Permissions Keep Prompting

**Symptoms:** Claude asks for permission on every command, even common ones.

**Solutions:**
1. Review `.claude/settings.json` and add patterns:
   ```json
   {
     "permissions": {
       "allow": [
         "Bash(npm test:*)",
         "Bash(npm run:*)",
         "Bash(git status:*)",
         "Bash(git diff:*)"
       ]
     }
   }
   ```
2. Use wildcard patterns: `"Bash(npm:*)"` allows all npm commands
3. Use Shift+Tab during development to auto-accept
4. Restart Claude Code after changing settings.json

### Slash Commands Not Working

**Symptoms:** `/command` doesn't do anything or shows "command not found".

**Solutions:**
1. Check `.claude/commands/` directory exists
2. Verify command file has `.md` extension: `command.md`
3. Commands are case-sensitive: `/Plan` ≠ `/plan`
4. Check file permissions: files must be readable
5. Verify markdown format is correct (title, instructions)
6. Run `/health` to diagnose configuration

### Context Getting Too Long

**Symptoms:** Claude seems confused, forgets earlier conversation, or responses slow down.

**Solutions:**
1. Start a new session for unrelated tasks
2. Use `/compact` to summarize and compress context
3. Be specific in requests - avoid "fix everything"
4. Break large tasks into smaller sessions
5. Use the Task tool for complex searches (Claude does this automatically)

### Claude Makes Incorrect Changes

**Symptoms:** Claude edits the wrong file or makes unintended modifications.

**Solutions:**
1. Always specify file paths explicitly
2. Use `/plan` before major changes to review approach
3. Keep git commits small and frequent for easy rollback
4. Review diffs before accepting: `git diff`
5. Add clear instructions in CLAUDE.md about file organization

### LLM Council Not Working

**Symptoms:** `/council` returns errors or says it's not configured.

**Solutions:**
1. Run `/council-config` to diagnose issues
2. Check `scripts/llm-council/config.yaml` exists (copy from `.example.yaml`)
3. Verify API keys in `.env`:
   ```bash
   # Check keys are set (don't show values)
   grep -c "API_KEY" .env
   ```
4. Ensure at least 2 providers have valid keys
5. Install dependencies: `pip install -r scripts/llm-council/requirements.txt`
6. Check Python is available: `python --version` or `python3 --version`

### Hooks Not Running

**Symptoms:** PostToolUse or PreToolUse hooks don't execute.

**Solutions:**
1. Verify hook syntax in `.claude/settings.json`:
   ```json
   {
     "hooks": {
       "PostToolUse": [
         {
           "matcher": "Edit",
           "hooks": [{ "type": "command", "command": "echo 'Hook ran'" }]
         }
       ]
     }
   }
   ```
2. Test the command manually to ensure it works
3. Check matcher pattern matches the tool (Edit, Write, Bash)
4. Restart Claude Code after changing hooks
5. Check for JSON syntax errors in settings file

### Git Operations Failing

**Symptoms:** Claude can't commit, push, or perform git operations.

**Solutions:**
1. Check git is configured: `git config --list`
2. Verify you're in a git repository: `git status`
3. Check remote is set: `git remote -v`
4. For push issues, verify authentication (SSH key or token)
5. Add git commands to permissions:
   ```json
   "Bash(git:*)"
   ```

### Upstream Sync Conflicts

**Symptoms:** Merge conflicts when pulling template updates.

**Solutions:**
1. Use `git status` to see conflicting files
2. Keep your CLAUDE.md - don't overwrite project-specific config
3. Cherry-pick specific files instead of merging all:
   ```bash
   git checkout upstream/main -- docs/BEST_PRACTICES.md
   ```
4. For complex conflicts, create a new branch:
   ```bash
   git checkout -b sync-upstream
   git merge upstream/main
   # Resolve conflicts
   git checkout main
   git merge sync-upstream
   ```

### Init Script Fails

**Symptoms:** `init-project.sh` or `init-project.ps1` errors.

**Solutions:**
1. **Linux/macOS:** Make executable: `chmod +x init-project.sh`
2. **Windows:** Run PowerShell as Administrator if needed
3. Check you're in the project root directory
4. Verify bash/PowerShell is available
5. Run manually step-by-step if script fails

### PDF Parser Not Working

**Symptoms:** `/parse-pdf` fails or produces errors.

**Solutions:**
1. Install dependencies:
   ```bash
   pip install -r scripts/pdf-parser/requirements.txt
   ```
2. Verify API key is set in `.env`:
   ```bash
   grep "ANTHROPIC_API_KEY\|OPENAI_API_KEY" .env
   ```
3. Check the PDF exists and is readable
4. For large PDFs, ensure sufficient disk space for temp files
5. Try with `--provider openai` if Anthropic fails
6. Run directly for detailed errors:
   ```bash
   python scripts/pdf-parser/parse_pdf.py your-file.pdf
   ```

### Performance Issues

**Symptoms:** Claude responses are slow or time out.

**Solutions:**
1. Check your internet connection
2. Large files slow down context - be specific about what to read
3. Use Haiku model for simple tasks (faster and cheaper)
4. Break complex tasks into smaller requests
5. Clear conversation and start fresh for new topics

---

## Next Steps

1. **Read the docs:**
   - [BEST_PRACTICES.md](BEST_PRACTICES.md) - Comprehensive Claude Code guidance
   - [UI_DESIGN_GUIDE.md](UI_DESIGN_GUIDE.md) - Better UI with design skills
   - [SKILLS_GUIDE.md](SKILLS_GUIDE.md) - Building specialized AI workflows

2. **Customize for your stack:**
   - Add language-specific linting commands
   - Configure framework-specific patterns
   - Document your testing conventions

3. **Iterate:**
   - Add memories with `#` as you work
   - Update CLAUDE.md when you find new patterns
   - Create custom commands for repetitive tasks

---

*Welcome to AI-assisted development. Build something great.*
