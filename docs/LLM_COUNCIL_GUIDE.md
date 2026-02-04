# LLM Council Guide

> An agentic advisory board for AI-assisted decision making.

## What is the LLM Council?

The LLM Council is an optional feature that allows you to consult multiple AI models when making decisions, evaluating plans, or breaking ties. Instead of relying on a single AI perspective, the council gathers diverse viewpoints and synthesizes them into a balanced recommendation.

**Inspired by**: [karpathy/llm-council](https://github.com/karpathy/llm-council)

### The Three-Stage Process

1. **Stage 1 - Gather Responses**: All council members independently answer your query in parallel
2. **Stage 2 - Peer Review**: Each model ranks others' responses anonymously (prevents bias)
3. **Stage 3 - Synthesis**: A "chairman" model produces a final, balanced recommendation

---

## When to Use the Council

### Ideal Use Cases

| Scenario | Example | Mode |
|----------|---------|------|
| **Architecture decisions** | "REST vs GraphQL for our API?" | `full` |
| **Technology choices** | "PostgreSQL vs MongoDB for this data model?" | `full` |
| **Implementation approaches** | "Should we use microservices or monolith?" | `full` |
| **Plan evaluation** | "Review this implementation plan for issues" | `full` |
| **Tie-breaking** | "Option A vs B vs C - which is best?" | `vote` |
| **Quick brainstorming** | "What caching strategies could work here?" | `quick` |

### When NOT to Use

- **Simple questions**: The council adds latency and cost
- **Project-specific context**: Claude (working in your codebase) often has better context
- **Urgent decisions**: Council queries take 30-60+ seconds
- **Subjective preferences**: "What color should the button be?"

---

## Setup

### Step 1: Install Dependencies

```bash
cd scripts/llm-council
pip install -r requirements.txt
```

### Step 2: Configure API Keys

Copy `.env.example` to `.env` and add your API keys:

```bash
# In project root
cp .env.example .env
```

Edit `.env`:

```bash
# At least 2 of these are required
ANTHROPIC_API_KEY=sk-ant-...    # https://console.anthropic.com/
OPENAI_API_KEY=sk-...           # https://platform.openai.com/api-keys
GOOGLE_AI_API_KEY=...           # https://aistudio.google.com/apikey
XAI_API_KEY=...                 # https://console.x.ai/
```

### Step 3: Configure Council (Optional)

Copy and customize the configuration:

```bash
cd scripts/llm-council
cp config.example.yaml config.yaml
```

Edit `config.yaml` to select your preferred models and settings.

### Step 4: Test

```bash
python scripts/llm-council/council.py --query "Hello, council!" --mode quick
```

---

## Usage

### From Claude Code

**Slash Command**:
```
/council Should we use REST or GraphQL for this API?
```

**Natural Language**:
```
I'm torn between these two approaches. Can you ask the council?
```

**Check Configuration**:
```
/council-config
```

### Command Line

```bash
# Quick mode (responses only)
python scripts/llm-council/council.py \
  --query "What are the tradeoffs of using Redis vs Memcached?" \
  --mode quick

# Full mode (with peer review)
python scripts/llm-council/council.py \
  --query "Evaluate this architecture: [details]" \
  --mode full

# Vote mode (for ranking)
python scripts/llm-council/council.py \
  --query "Rank these options: A) ..., B) ..., C) ..." \
  --mode vote
```

### Programmatic (from your code)

```python
import subprocess

result = subprocess.run([
    "python", "scripts/llm-council/council.py",
    "--query", "Which database should we use?",
    "--mode", "vote"
], capture_output=True, text=True)

# Parse the Markdown output
council_response = result.stdout
```

---

## Configuration Reference

### config.yaml Structure

```yaml
council:
  # Who sits on the council
  members:
    - provider: anthropic
      model: claude-sonnet-4-20250514
      name: "Claude Sonnet"        # Display name
    - provider: openai
      model: gpt-4o
      name: "GPT-4o"
    - provider: google
      model: gemini-2.0-flash
      name: "Gemini 2.0"

  # Who synthesizes the final answer
  chairman:
    provider: anthropic
    model: claude-sonnet-4-20250514
    name: "Chairman"

# Save money on Stage 2
cost_optimization:
  use_fast_models_for_review: true
  fast_model_overrides:
    anthropic: claude-3-5-haiku-latest
    openai: gpt-4o-mini
    google: gemini-2.0-flash

defaults:
  mode: full
  timeout_seconds: 60
  max_retries: 2
```

### Supported Providers

| Provider | Env Variable | Models | Pricing |
|----------|--------------|--------|---------|
| **Anthropic** | `ANTHROPIC_API_KEY` | claude-opus-4, claude-sonnet-4, claude-3-5-haiku | [Pricing](https://anthropic.com/pricing) |
| **OpenAI** | `OPENAI_API_KEY` | gpt-4o, gpt-4o-mini, o1, o1-mini | [Pricing](https://openai.com/pricing) |
| **Google** | `GOOGLE_AI_API_KEY` | gemini-2.0-flash, gemini-1.5-pro | [Pricing](https://ai.google.dev/pricing) |
| **xAI** | `XAI_API_KEY` | grok-2, grok-2-mini | [Pricing](https://x.ai/api) |

---

## Cost Management

### Estimated Costs Per Query

| Mode | API Calls | Est. Cost* | Notes |
|------|-----------|-----------|-------|
| `quick` | 3-4 | $0.01-0.05 | Responses only |
| `full` | 7-9 | $0.03-0.15 | With peer review (fast models) |
| `vote` | 4-5 | $0.02-0.08 | Ranking only |

*With cost optimization enabled. Premium models (Opus, GPT-4) can be 5-10x higher.

### Cost Optimization Strategies

1. **Use fewer members**: 2-3 models often sufficient
   ```yaml
   council:
     members:
       - provider: anthropic
         model: claude-3-5-haiku-latest
       - provider: openai
         model: gpt-4o-mini
   ```

2. **Enable fast model overrides**: Cheaper models for peer review
   ```yaml
   cost_optimization:
     use_fast_models_for_review: true
   ```

3. **Use `quick` mode**: Skip peer review for non-critical queries
   ```bash
   python council.py --query "..." --mode quick
   ```

4. **Choose efficient models**: Haiku, GPT-4o-mini, Gemini Flash

### Budget Configuration Example

```yaml
# Minimal cost configuration
council:
  members:
    - provider: anthropic
      model: claude-3-5-haiku-latest
      name: "Claude Haiku"
    - provider: openai
      model: gpt-4o-mini
      name: "GPT-4o Mini"
  chairman:
    provider: anthropic
    model: claude-3-5-haiku-latest
```

---

## Performance Expectations

### Response Times by Mode

| Mode | Typical Time | API Calls | Best For |
|------|--------------|-----------|----------|
| `quick` | 5-15 seconds | 3-4 | Fast brainstorming, simple questions |
| `full` | 30-60 seconds | 7-9 | Important decisions, thorough analysis |
| `vote` | 15-30 seconds | 4-5 | Ranking options, tie-breaking |

*Times vary based on model selection, query complexity, and API response times.*

### Factors Affecting Performance

1. **Model selection**: Fast models (Haiku, GPT-4o-mini) respond in 2-5s; premium models (Opus, GPT-4) take 5-15s
2. **Query length**: Longer queries = longer processing time
3. **Provider latency**: Some providers have faster APIs than others
4. **Parallel execution**: Stage 1 runs all members in parallel; Stage 2 runs sequentially

### Optimizing for Speed

```yaml
# Fast configuration (~10s for full mode)
council:
  members:
    - provider: anthropic
      model: claude-3-5-haiku-latest
    - provider: openai
      model: gpt-4o-mini
  chairman:
    provider: anthropic
    model: claude-3-5-haiku-latest

cost_optimization:
  use_fast_models_for_review: true
```

### When Speed Matters

- Use `quick` mode for time-sensitive decisions
- Reduce council to 2 members
- Choose the fastest models available
- Consider if you really need the council (Claude alone is often faster)

---

## Output Format

The council outputs Markdown for easy reading:

```markdown
# LLM Council Results

## Query
> Should we use REST or GraphQL for our API?

## Stage 1: Individual Responses

### Claude Sonnet
REST provides better caching, simpler debugging...

### GPT-4o
GraphQL offers flexibility for frontend teams...

### Gemini 2.0
Consider your team's experience...

## Stage 2: Peer Review Rankings

| Model | Aggregate Score |
|-------|-----------------|
| Claude Sonnet | 8 |
| GPT-4o | 7 |
| Gemini 2.0 | 6 |

## Stage 3: Chairman Synthesis

Based on the council's deliberation, **REST is recommended**
for your initial API implementation...

---
*Council consulted: 2025-01-15 14:30:22*
*Mode: full*
*Members: Claude Sonnet, GPT-4o, Gemini 2.0*
```

---

## Adding New Providers

The council uses a modular provider system. To add a new provider:

### 1. Create Provider File

Create `scripts/llm-council/providers/newprovider.py`:

```python
from typing import Optional
import httpx
from .base import BaseProvider, ProviderResponse

class NewProvider(BaseProvider):
    PROVIDER_NAME = "newprovider"
    ENV_KEY_NAME = "NEWPROVIDER_API_KEY"
    API_URL = "https://api.newprovider.com/v1/chat"

    async def complete(
        self,
        prompt: str,
        model: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> ProviderResponse:
        # Implement API call
        ...
```

### 2. Register Provider

Add to `providers/__init__.py`:

```python
from .newprovider import NewProvider
__all__ = [..., "NewProvider"]
```

Add to `council.py`:

```python
PROVIDERS = {
    ...,
    "newprovider": NewProvider,
}
```

### 3. Add to Config

```yaml
council:
  members:
    - provider: newprovider
      model: their-model-name
      name: "Display Name"
```

---

## Troubleshooting

### "Need at least 2 council members"

You need API keys for at least 2 providers. Check:
```bash
/council-config
```

### Timeout Errors

- Increase `timeout_seconds` in config.yaml
- Use faster models (Haiku, GPT-4o-mini, Gemini Flash)
- Reduce query complexity

### Rate Limit Errors

- Add delays between council queries
- Use providers with higher rate limits
- Consider reducing council size

### API Key Issues

Verify keys are set correctly:
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('ANTHROPIC:', 'Set' if os.getenv('ANTHROPIC_API_KEY') else 'Not set')"
```

---

## Best Practices

1. **Be specific**: "Should we use X or Y for [specific use case]?" beats "What's better, X or Y?"

2. **Provide context**: Include relevant details about your project, constraints, requirements

3. **Use appropriate mode**:
   - `quick` for brainstorming
   - `full` for important decisions
   - `vote` for ranking options

4. **Trust but verify**: The council provides input; you (and Claude with codebase context) make the final call

5. **Consider cost**: Not every decision needs the council; reserve it for important choices

---

## Philosophy

The LLM Council embodies the idea that diverse AI perspectives can lead to better decisions than any single model. By combining:

- **Multiple viewpoints**: Different training, different biases, different strengths
- **Peer review**: Quality signal through cross-evaluation
- **Synthesis**: Balanced recommendation considering all perspectives

You get a more robust advisory process for important technical decisions.

However, remember that the council lacks your project's specific context. Claude, working directly in your codebase, often has insights the council cannot. Use the council as one input among many, not as the final word.

---

## Resources

- [karpathy/llm-council](https://github.com/karpathy/llm-council) - Original inspiration
- [Anthropic API Docs](https://docs.anthropic.com/)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Google AI Docs](https://ai.google.dev/docs)
- [xAI API Docs](https://docs.x.ai/)
