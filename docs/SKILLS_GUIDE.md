# Claude Skills Guide

> Building specialized "digital employees" for repeatable, deterministic tasks.

## What Are Claude Skills?

Skills are **automated workflows** that:
- Follow specific constraints, guidelines, and steps you define
- Load context only when relevant (avoiding context bloat)
- Can run scripts/code for deterministic calculations
- Are repeatable and consistent across uses

Think of skills as **training a junior teammate** with specific guardrails and instructions.

---

## Skills vs Projects vs Sub-Agents

| Feature | Projects | Sub-Agents | Skills |
|---------|----------|------------|--------|
| **Scope** | Workspace with instructions | Multi-workflow parallel tasks | Specialized single tasks |
| **Context** | All loaded upfront | Isolated to conversation | Loaded only when needed |
| **Determinism** | LLM interprets | LLM interprets | Scripts ensure accuracy |
| **Best for** | Team collaboration | Complex parallel work | Repeatable specialized tasks |
| **Location** | Claude.ai | Claude Code | Both |

### When to Use Each

**Use Projects when:**
- Collaborating with team members
- Need persistent workspace with shared context
- Working on varied tasks within a domain

**Use Sub-Agents when:**
- Breaking complex tasks into parallel work
- Need specialized agents (frontend, backend, etc.)
- Working in Claude Code on multi-step implementations

**Use Skills when:**
- Task is repeatable and specialized
- Need consistent, deterministic output
- Want to avoid context overload
- Need accurate calculations (not LLM guessing)

---

## The Context Problem Skills Solve

### Context Rot
Research shows that **too much context degrades LLM performance**:
- More hallucination
- Less accurate outputs
- Slower responses
- Higher costs

### How Skills Help
- **Load context only when relevant** to the specific task
- Like giving a coworker just enough info, not overwhelming them
- Keep instructions focused and bounded

---

## Skill Architecture

```
my-skill/
├── skill.md           # Main instructions and task definition
├── references/        # Additional context files
│   ├── glossary.md   # Domain terms and definitions
│   ├── examples.md   # Example outputs to match
│   └── guidelines.md # Brand/style guidelines
└── scripts/          # Deterministic code
    ├── analyze.py    # Data analysis scripts
    └── calculate.py  # Calculation scripts
```

### skill.md Structure

```markdown
# Skill Name

## Overview
Brief description of what this skill does.

## When to Use
Describe the scenarios where this skill should be invoked.

## Instructions
1. Step-by-step process
2. Specific guidelines to follow
3. Constraints and boundaries

## Input Requirements
- What the user needs to provide
- Expected formats

## Output Format
- How results should be structured
- Templates or examples

## Scripts
Reference any scripts that should run:
- See scripts/analyze.py for data processing
- See scripts/calculate.py for metrics

## References
- See references/glossary.md for term definitions
- See references/examples.md for output examples
```

---

## Creating Skills

### Method 1: Use Skill Creator

```
I just added the skill creator skill.
Can you make me a skill that [description of what you want]?
```

### Method 2: Manual Creation

1. Create skill directory structure
2. Write skill.md with clear instructions
3. Add reference files for context
4. Write scripts for calculations
5. Upload to Claude

### Best Practices for Skill Creation

**Be Specific:**
```
❌ "Analyze marketing data"
✅ "Calculate ROAS by dividing revenue by spend,
    segment by channel, flag any channel with
    ROAS < 2.0 as underperforming"
```

**Include Scripts for Math:**
```python
# Don't let the LLM guess calculations
def calculate_roas(revenue, spend):
    return revenue / spend if spend > 0 else 0

def calculate_cac(spend, conversions):
    return spend / conversions if conversions > 0 else float('inf')
```

**Provide Reference Examples:**
- Include examples of expected output format
- Show tone/style for content generation
- Define domain-specific terms

---

## Example Skills

### 1. Marketing Analytics Skill

**Purpose:** Analyze campaign data with accurate calculations

**skill.md excerpt:**
```markdown
## Instructions
1. Load the provided CSV data
2. Run scripts/analyze.py for calculations
3. Generate insights based on metrics

## Scripts
- calculate_roas(): Revenue / Spend
- calculate_cac(): Spend / Conversions
- calculate_conversion_rate(): Conversions / Clicks

## Output Format
- Overall performance summary
- Channel breakdown with metrics
- Top/bottom performers
- Recommendations
```

**Why it works:** Scripts ensure calculations are accurate, not hallucinated.

### 2. A/B Test Generator Skill

**Purpose:** Generate experiment ideas for websites

**skill.md excerpt:**
```markdown
## Instructions
1. Scrape the provided URL using firecrawl
2. Analyze current page structure
3. Generate experiment ideas using ICE framework
4. Prioritize by Impact, Confidence, Ease

## Output Format
| Experiment | Control | Variant | Impact | Confidence | Ease | ICE Score |
```

**Why it works:** Structured framework ensures consistent, actionable output.

### 3. Content Transformer Skill

**Purpose:** Transform tweets into newsletter content

**skill.md excerpt:**
```markdown
## Instructions
1. Read the provided tweet
2. Reference examples/newsletter-style.md for tone
3. Expand into long-form content
4. Match the newsletter format

## References
- examples/newsletter-style.md: Example newsletters for tone matching
- guidelines/brand-voice.md: Brand voice guidelines
```

**Why it works:** Reference files ensure consistent style and tone.

---

## Skills in Claude Code

### Installing Skills

```bash
# Add skill marketplace
/add-skill-marketplace https://skills.anthropic.com

# Install a skill
/install-skill [skill-name]

# List installed skills
/skills
```

### Using Skills

```
Use the [skill-name] skill to [task description].
```

Example:
```
Use the front-end design skill to improve the design of this landing page.
```

### Pre-installed Skills

- **Artifact Builder**: Create functional web apps
- **MCP Builder**: Create MCP servers
- **Skill Creator**: Create new skills (meta!)

---

## Building "Digital Employees"

Skills enable you to create specialized AI workers:

### Marketing Analyst
- Skills: Campaign analyzer, A/B test generator, report builder
- Reference files: KPI definitions, brand guidelines
- Scripts: ROAS calculator, attribution models

### Content Writer
- Skills: Tweet-to-blog converter, newsletter generator
- Reference files: Style guide, tone examples, past content
- Scripts: Word count validator, SEO checker

### Data Analyst
- Skills: CSV analyzer, dashboard generator
- Reference files: Metric definitions, business glossary
- Scripts: Statistical calculations, data transformations

### Code Reviewer
- Skills: Security auditor, performance analyzer
- Reference files: Coding standards, security checklist
- Scripts: Linting, complexity analysis

---

## Troubleshooting

### Skill Not Giving Expected Output?

1. **Check instructions clarity**: Are they specific enough?
2. **Add more reference files**: Examples help calibrate output
3. **Use scripts for calculations**: Don't rely on LLM math
4. **Reduce scope**: Focused skills work better than broad ones

### Context Overload?

- Split into multiple focused skills
- Load references only when needed
- Keep skill.md concise

### Inconsistent Results?

- Add more examples to references
- Be more prescriptive in instructions
- Include output templates

---

## The Future of Skills

Skills represent a shift toward:
- **Deterministic AI workflows** where you control the process
- **Composable AI systems** where skills can chain together
- **AI fluency** where humans define the guardrails

The key insight: **AI adoption struggles because of prompting, not AI capability.**
Skills solve this by encoding expertise into reusable, consistent workflows.

---

## Resources

- [Claude Skills Documentation](https://docs.anthropic.com/skills)
- [Skill Marketplace](https://skills.anthropic.com)
- [MCP Documentation](https://modelcontextprotocol.io)

---

*This guide synthesizes best practices from Anthropic documentation and community expertise.*
