# LLM Council

An "agentic advisory board" that consults multiple AI models for decision-making, plan evaluation, and tie-breaking.

Based on [karpathy/llm-council](https://github.com/karpathy/llm-council).

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy `.env.example` to `.env` in the project root and add your API keys:

```bash
# At least 2 of these are required
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_AI_API_KEY=...
XAI_API_KEY=...
```

### 3. Configure Council (Optional)

Copy the example config and customize:

```bash
cp config.example.yaml config.yaml
```

### 4. Run

```bash
# Quick query (responses only)
python council.py --query "Should we use REST or GraphQL?" --mode quick

# Full deliberation (with peer review)
python council.py --query "Evaluate this architecture decision" --mode full

# Voting mode (for ranking options)
python council.py --query "Option A vs Option B vs Option C" --mode vote
```

## How It Works

The council uses a three-stage deliberation process:

### Stage 1: Gather Responses
All configured council members independently answer your query in parallel.

### Stage 2: Peer Review
Each model reviews and ranks the other models' responses anonymously. This prevents bias and provides quality signals.

### Stage 3: Chairman Synthesis
A designated "chairman" model synthesizes all responses and rankings into a final, balanced recommendation.

## Modes

| Mode | Stages | Use Case | Cost |
|------|--------|----------|------|
| `quick` | 1 only | Simple questions, brainstorming | $ |
| `full` | 1, 2, 3 | Important decisions, architecture | $$$ |
| `vote` | 1, 2 | Ranking options, tie-breaking | $$ |

## Configuration

### config.yaml

```yaml
council:
  members:
    - provider: anthropic
      model: claude-sonnet-4-20250514
      name: "Claude Sonnet"
    - provider: openai
      model: gpt-4o
      name: "GPT-4o"
    # Add more members...

  chairman:
    provider: anthropic
    model: claude-sonnet-4-20250514

cost_optimization:
  use_fast_models_for_review: true
  fast_model_overrides:
    anthropic: claude-3-5-haiku-latest
    openai: gpt-4o-mini
```

### Supported Providers

| Provider | Env Variable | Example Models |
|----------|--------------|----------------|
| Anthropic | `ANTHROPIC_API_KEY` | claude-opus-4, claude-sonnet-4, claude-3-5-haiku |
| OpenAI | `OPENAI_API_KEY` | gpt-4o, gpt-4o-mini, o1, o1-mini |
| Google | `GOOGLE_AI_API_KEY` | gemini-2.0-flash, gemini-1.5-pro |
| xAI | `XAI_API_KEY` | grok-2, grok-2-mini |

## Usage from Claude Code

Use the `/council` slash command:

```
/council Should we use microservices or a monolith?
```

Or ask naturally:

```
Can you consult the council about the database schema options?
```

## Programmatic Usage

```python
import subprocess
import json

result = subprocess.run(
    ["python", "scripts/llm-council/council.py",
     "--query", "Which caching strategy?",
     "--mode", "vote"],
    capture_output=True,
    text=True
)

print(result.stdout)  # Markdown-formatted council results
```

## Cost Optimization

The council can get expensive with premium models. To reduce costs:

1. **Use fewer members**: 2-3 models is often sufficient
2. **Enable fast model overrides**: Uses cheaper models for peer review
3. **Use `quick` mode**: Skips peer review stage entirely
4. **Choose efficient models**: Haiku, GPT-4o-mini, Gemini Flash are cost-effective

## Adding New Providers

1. Create a new file in `providers/` (e.g., `providers/newprovider.py`)
2. Implement the `BaseProvider` interface
3. Add to `providers/__init__.py`
4. Add to `PROVIDERS` dict in `council.py`

See existing providers for examples.

## Troubleshooting

### "Need at least 2 council members"
Set API keys for at least 2 providers in your `.env` file.

### Timeout errors
Increase `timeout_seconds` in config.yaml or use faster models.

### Rate limit errors
Add delays between queries or use models with higher rate limits.

## License

MIT - See project root LICENSE file.
