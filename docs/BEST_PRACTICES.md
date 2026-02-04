# Claude Code Best Practices

> Synthesized from Anthropic documentation, expert guidance, and field experience.

## Understanding Claude Code

### How It Works
Claude Code is a **pure agent** architecture:
- Instructions + powerful tools + model running in a loop until completion
- No indexing or RAG - uses agentic search (glob, grep, find) to explore codebases
- 200K token context window with `/clear` and `/compact` for management
- Lightweight permission system for dangerous operations

### Mental Model
Think of Claude Code as a skilled terminal-native coworker who:
- Explores codebases the way a new team member would
- Uses standard tools (git, grep, find) rather than magic indexing
- Works iteratively, searching and refining understanding
- Can be interrupted and redirected at any time

---

## Configuration Best Practices

### CLAUDE.md Files

**Purpose**: Primary way to share state across sessions and team members.

**Locations** (in order of precedence):
1. Project root (`./CLAUDE.md`) - shared via version control
2. Home directory (`~/.claude/CLAUDE.md`) - personal defaults
3. Subdirectories - read by Claude when relevant, not auto-loaded

**Hierarchical Structure**: CLAUDE.md files can be nested. Place them in subdirectories for module-specific instructions. The most specific (most nested) file takes priority when Claude is working in that directory.

**Content Guidelines**:
- Keep it focused and concise
- Update when switching model versions
- Include only what Claude needs to know
- Remove outdated instructions

**Essential Sections**:
```markdown
## Project Overview
Brief description of what this project does

## Development Commands
How to build, test, lint, run

## Code Style
Specific conventions for this project

## Architecture
High-level structure and patterns
```

**Quick Memory Addition**: Use `#` to quickly add to memory:
```
# always use TypeScript strict mode
# prefer functional components over class components
```
Claude will save to the most relevant CLAUDE.md file.

### D.R.Y. - Don't Repeat Yourself

**Build a command library** for repetitive prompts:
- Creating API endpoints with your middleware pattern
- Running linter and fixing all errors
- Generating boilerplate with your conventions

Organize commands into subdirectories as your library grows:
```
.claude/commands/
├── api/
│   ├── endpoint.md
│   └── middleware.md
├── testing/
│   └── coverage.md
└── deploy/
    └── staging.md
```

**Useful command repos to explore:**
- Search GitHub for "claude code commands" for community libraries

### Permission Management

**Speed up workflows by pre-approving safe commands**:
```json
{
  "permissions": {
    "allow": [
      "Read(*)",
      "Glob(*)",
      "Grep(*)",
      "Bash(git status:*)",
      "Bash(npm test:*)",
      "Bash(npm run lint:*)"
    ]
  }
}
```

**Permission Modes**:
- **Default**: Asks permission for writes and bash commands
- **Shift+Tab**: Auto-accept mode for current session
- **`--dangerously-skip-permissions`**: Skip all permission checks (use with caution)

See `.claude/settings.example.json` for comprehensive permission patterns.

### Hooks

Hooks run commands before/after Claude's tool use:

**PreToolUse**: Runs before tool executes (return non-zero to block)
**PostToolUse**: Runs after tool executes (good for validation)

**Common patterns**:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit",
        "hooks": [{ "type": "command", "command": "npx prettier --write $CLAUDE_FILE_PATH" }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [{ "type": "command", "command": "npx tsc --noEmit" }]
      }
    ]
  }
}
```

---

## Workflow Best Practices

### Clear Aggressively
**Every time you start something new, use `/clear`.**

Don't let context build up with irrelevant history:
- Compaction runs an LLM call to summarize (takes time)
- Old context can confuse new tasks
- Start fresh for unrelated work

**When to use each**:
- `/clear`: Starting new task, switching context
- `/compact`: Continuing related work, need history

### Message Queuing
Queue multiple prompts while Claude works:
- Type your next prompt while Claude is busy
- Claude intelligently runs them when appropriate
- Won't auto-run if feedback is needed
- Great for batching related tasks

### Brainstorm → Plan → Execute
The most effective workflow has three phases:

**1. Brainstorm** (optional but powerful):
```
"I want to add a folder system. What are different options for designing this?
What are different cool features we could add?"
```
Bounce ideas off Claude before committing to an approach.

**2. Plan** (Shift+Tab twice):
```
"Perfect, implement option 3 please."
```
Let Sonnet create a detailed plan.

**3. Execute**:
Approve the plan and let Claude implement.

### Simple Prompts Win
**Prompt engineering is overrated.** The models are smart enough.

```
❌ Complex structured prompts with context/UI/database sections
✅ "I want a folder system in the app so I can put entries into folders"
```

Just tell Claude what you want. In plan mode, it figures out the context.

### Test-Driven Development
1. Write or verify tests exist
2. Make small changes
3. Run tests after each change
4. Commit when tests pass
5. Repeat

### Using the Todo List
- Watch for items that don't make sense
- Press `Escape` to redirect if Claude is off track
- Use todos for visibility into Claude's plan

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Escape` | Stop Claude (not Ctrl+C!) |
| `Escape` twice | Jump to previous messages |
| `Shift+Tab` | Auto-accept mode |
| `Ctrl+V` | Paste images (Mac: not Cmd+V) |
| `Shift+drag` | Drag files into terminal (VS Code) |
| `Up arrow` | Access past chats (including prior sessions) |
| `Shift+Enter` | New line (after terminal setup) |

---

## Advanced Techniques

### Multiple Claude Instances
Run 2-4 instances for parallel work:
- Different features in different terminals
- Use shared markdown files for coordination
- Example: Write to `ticket.md` for context passing
- Works on different parts of codebase/different files

### Sub-Agents: Tasks, Not Roles

**What doesn't work well:**
- Assigning roles (frontend dev, designer, product manager)
- Expecting autonomous brainstorming like humans

**What works well - define agents for specific tasks:**
- Code cleanup and optimization
- Documentation generation
- Research/data gathering from web
- UI/UX review (with Playwright MCP)

**Creating sub-agents:**
```
/agents → Create new agent → Project/Personal → Generate with Claude → Describe task → Set permissions → Save
```

Invoke with `@agent-name` or natural language.

**Why this works:** Each sub-agent gets its own context window, reducing pollution of the main context. They're great for offloading specific tasks while maintaining quality.

### Escape Key Mastery
- **Single Escape**: Stop and redirect
- **Double Escape**: Jump back in conversation history, see previous messages
- Know when to escape vs. let Claude figure it out

### Screenshot-Driven Development
Claude is multimodal:
- Paste screenshots for visual debugging (use Ctrl+V, not Cmd+V on Mac)
- Reference mock images: "Build this UI from mock.png"
- Use for error screenshots, design specs

**For UI work, always include visual references:**
- Use [Dribbble](https://dribbble.com) for UI design inspiration
- Use [V0.dev](https://v0.dev) design system for components
- Pinterest has great app design inspiration
- Screenshot and paste (Cmd+Ctrl+Shift+4 on Mac copies to clipboard)
- Claude's default UI tends toward purple gradients - references help

### Front-End Design Skill
Install the front-end design skill for dramatically better UI:

```bash
# Add marketplace and install
/add-skill-marketplace https://skills.anthropic.com
/install-skill front-end-design
```

**Usage:**
```
Use the front-end design skill to improve the design of this page.
```

Or with a reference:
```
Use the front-end design skill to redesign this following the attached screenshot.
[paste screenshot from Dribbble]
```

**The "Black, White, and One Color" Rule:**
Start every design with black, white, and one accent color. Add more colors only after establishing this foundation.

See [docs/UI_DESIGN_GUIDE.md](UI_DESIGN_GUIDE.md) for comprehensive UI/design guidance.

### Extended Thinking
For complex problems, add "think hard" to prompts:
```
"Think hard about this bug. Search the codebase,
understand the data flow, and explain what's causing it."
```

### Custom Slash Commands
Create `.claude/commands/[name].md`:
```markdown
# Command Title

Do something with: $ARGUMENTS

## Instructions
1. Step one
2. Step two
```

Use subfolders: `.claude/commands/builder/plugin.md` → `/builder:plugin`

### Claude Skills
Skills are **specialized automated workflows** that:
- Load context only when relevant (avoiding context bloat)
- Can run scripts for deterministic calculations
- Are repeatable and consistent

**Installing Skills:**
```bash
/add-skill-marketplace https://skills.anthropic.com
/install-skill [skill-name]
```

**Using Skills:**
```
Use the [skill-name] skill to [task description].
```

**Key Skills:**
- **Artifact Builder**: Create functional web apps
- **Skill Creator**: Create new skills
- **Front-End Design**: Better UI design

**When to use skills vs sub-agents:**
- Skills: Repeatable specialized tasks, need deterministic output
- Sub-agents: Complex parallel work, breaking down large tasks

See [docs/SKILLS_GUIDE.md](SKILLS_GUIDE.md) for building custom skills and "digital employees."

### Plugins: Clone Entire Setups
Plugins bundle commands, agents, MCP servers, and skills into shareable packages:

```bash
# Add a plugin marketplace
/add-plugin-marketplace [url]

# Install plugins from marketplace
/plugins
```

This lets you clone a power user's entire workflow with a single command.

---

## GitHub Integration

### Automatic PR Code Review
1. Run `/install-github-app` in Claude Code
2. Customize `.github/workflows/claude-code-review.yaml`

**Recommended prompt** (focused on what matters):
```yaml
prompt: |
  Review for bugs and security issues only.
  Do NOT comment on style, naming, or refactoring.
  Be concise. If code looks good, just say "LGTM".
```

### PR Workflow
Claude can:
- Review PRs and address comments
- Create PRs with descriptions
- Push commits addressing feedback

---

## Model Selection

### Default Behavior
- Uses Opus until 50% usage, then switches to Sonnet
- Good for cost efficiency

### Manual Selection
- `/model` - Check/change current model
- Opus: Better quality, not noticeably slower than Sonnet 4
- Sonnet: More cost-efficient, still very capable

### Cost-Efficient Strategy: Haiku for Implementation
Select Haiku model (`/model` → Haiku) for a powerful cost-saving approach:
- **Sonnet still handles planning** (Shift+Tab twice for plan mode)
- **Haiku handles implementation** (execution of the plan)
- Works well because detailed plans don't need the smartest model to execute
- Significant token/credit savings with minimal quality loss

---

## Integration Tips

### CLI Tools vs MCP Servers
**Prefer CLI tools** when:
- Tool is well-known and documented
- Examples: `gh` (GitHub), `docker`, `aws`

**Use MCP servers** when:
- Need custom integrations
- CLI doesn't exist or is limited
- Need structured data exchange

### Recommended MCP Servers

| Server | Purpose | Usage |
|--------|---------|-------|
| **Context7** | Up-to-date library docs | "use context7" in prompts |
| **Supabase** | Database queries, migrations | Direct DB access |
| **Playwright** | Browser automation, DOM inspection | Front-end debugging |
| **Chrome DevTools** | Console logs, debugging | Front-end testing |
| **Stripe** | Payment integration | Billing features |

**Context7 is especially valuable** - solves the "outdated training data" problem by fetching latest documentation for popular libraries.

### Git Integration
Claude excels at:
- Writing commit messages and PR descriptions
- Understanding code history (`git log`, `git blame`)
- Resolving merge conflicts
- Managing rebases

Tell Claude about sticky situations:
```
"I'm in the middle of a rebase with conflicts.
Help me resolve them and continue."
```

---

## The "Keep It Simple" Philosophy

**Claude Code works out of the box for 99.9% of use cases.**

### You Probably Don't Need
- 40 custom sub-agents
- 20 MCP servers
- 30 custom slash commands
- Complex prompt engineering templates

### What Actually Matters
- A good CLAUDE.md with your project's commands and patterns
- Clear, simple prompts telling Claude what you want
- Plan mode for significant changes
- Screenshots for UI work

### The Models Are Smart
Sonnet 4.5 can:
- Find documentation on its own (even for brand-new APIs)
- Understand your codebase structure
- Figure out context without elaborate prompts
- Call sub-agents automatically when needed

Don't over-engineer your setup. Start simple, add complexity only when needed.

---

## Productive Downtime

**80% of vibe coding is waiting.** Use it wisely.

### Don't Waste Wait Time
❌ Scrolling social media
❌ Playing games
❌ Context-switching to unrelated work

### Productive Alternatives
✅ **Have a second AI chat open** as your "co-pilot/CEO/product manager"
- Brainstorm features and roadmap
- Plan marketing and launch strategy
- Think through architecture decisions
- Get advice on non-coding decisions

✅ **Queue your next prompts** while Claude works

✅ **Review Claude's todo list** to catch issues early

This compounds: if you're productive during the 80% wait time, you're effectively 5x more productive than someone who doom-scrolls.

---

## Anti-Patterns to Avoid

### Over-Prompting
❌ Repeating instructions already in CLAUDE.md
✅ Trust that CLAUDE.md is loaded and followed

### Context Bloat
❌ Letting context fill up without clearing
✅ `/clear` for new tasks, `/compact` only when you need history

### Micro-Management
❌ Approving every single file read
✅ Configure permissions for read operations

### Ignoring the Todo List
❌ Not watching what Claude plans to do
✅ Review todo items, escape if off-track

### Skipping Tests
❌ "Just implement it, we'll test later"
✅ "Implement with tests, verify they pass"

### Waiting on Idle Agents
❌ Coming back to find Claude waiting for permission
✅ Use `--dangerously-skip-permissions` or configure permissions

### Letting AI Make You Lazy
❌ Skipping code review for AI-generated code
✅ Review for security, performance, error handling before production

**Garbage in = garbage out**: If you can't write a clear prompt, you don't know what you want. The AI definitely won't either.

**AI generates code, but humans own it**: Start a new session asking Claude to review the files it touched. Speed means nothing if your app is buggy or insecure.

---

## Large Codebase Tips

Claude Code handles large codebases exceptionally well:
- No issues with very large files (tested with 18,000+ line files)
- Excellent at navigating complex codebases
- Good at understanding relationships between components
- Rarely gets stuck compared to other tools

---

## Treat Claude as a Creative Partner

Claude isn't just a code generator - it's a thinking partner.

### Before Coding, Brainstorm
```
"I want to add X feature. What are different options for designing this?
What are different cool features we could add?"
```

### Ask for Opinions
- "What do you think about this approach?"
- "What would you change?"
- "What are the tradeoffs?"

### Let Claude Surprise You
Claude often suggests approaches you hadn't considered. The tag-based system vs. folders example: sometimes the AI's alternative is better than your original idea.

---

## Sources

This document synthesizes best practices from:
- Anthropic official documentation and talks
- Claude Code team recommendations (Cal's May 2025 talk)
- Builder.io tips and tricks
- Alex Finn's lessons learned (extensive daily usage)
- 800+ hours practitioner experience (sub-agents, MCP servers, plugins)
- Amir's digital employees tutorial (Claude Skills)
- Chris's front-end design skill demo
- Community patterns and experiences

*Last updated: December 2024*
