# Plan Agentic Workflow

Help the user design an agentic solution for their requirements.

## Instructions

When the user invokes `/agent-plan`, guide them through designing an agentic workflow:

### 1. Understand the Goal

Ask about:
- What task needs to be automated?
- How long will it run? (minutes, hours, days)
- What tools/integrations are needed?
- What does success look like?

### 2. Recommend Pattern

Based on the requirements, recommend one of these patterns:

| Pattern | Best For | Complexity |
|---------|----------|------------|
| **Sub-Agent** | Single complex subtask needing isolated context | Low |
| **Skill** | Repeatable workflow that should run consistently | Medium |
| **LLM Council** | Important decisions needing diverse perspectives | Low |
| **Long-Running Agent** | Multi-session tasks spanning hours/days | High |
| **Agent SDK** | Production integration, programmatic control | High |

### 3. Design State Management

For the chosen pattern, define:
- What progress needs tracking?
- What files should persist state?
- How to checkpoint and recover?
- What constitutes completion?

### 4. Security Considerations

Address:
- What commands should be allowed?
- What filesystem access is needed?
- What external services to connect?
- What validation hooks are needed?

### 5. Output Plan

Provide a structured plan including:

```
## Agentic Workflow Plan

### Overview
[Brief description]

### Pattern: [Chosen Pattern]
[Justification]

### State Management
- Progress file: [filename]
- Task tracking: [approach]
- Checkpointing: [strategy]

### Security
- Allowed commands: [list]
- Filesystem scope: [paths]
- Hooks: [validation needs]

### Implementation Steps
1. [Step 1]
2. [Step 2]
...

### Success Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
```

## Reference Documentation

- Agentic patterns: `docs/AGENTIC_GUIDE.md`
- Agent SDK: `docs/AGENT_SDK_QUICKSTART.md`
- Skills: `docs/SKILLS_GUIDE.md`
- LLM Council: `docs/LLM_COUNCIL_GUIDE.md`
- Working examples: `scripts/agent-examples/`

---

$ARGUMENTS contains the user's agentic requirements or questions.
