# LLM Council Configuration

Check and manage the LLM Council configuration.

## Instructions

### 1. Check Configuration Status

Check if the council is properly configured:

```bash
# Check if config file exists
ls scripts/llm-council/config.yaml 2>/dev/null || echo "Config file not found"

# Check for .env file
ls .env 2>/dev/null || echo ".env file not found"
```

### 2. Validate API Keys

Check which providers have API keys configured (without revealing the actual keys):

```bash
# Check environment variables (show only if set, not the values)
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

providers = {
    'Anthropic': 'ANTHROPIC_API_KEY',
    'OpenAI': 'OPENAI_API_KEY',
    'Google AI': 'GOOGLE_AI_API_KEY',
    'xAI': 'XAI_API_KEY',
}

print('API Key Status:')
print('-' * 30)
configured = 0
for name, key in providers.items():
    value = os.getenv(key)
    if value and len(value) > 0:
        print(f'  {name}: Configured')
        configured += 1
    else:
        print(f'  {name}: Not set')

print('-' * 30)
print(f'Total: {configured}/4 providers configured')
if configured < 2:
    print('WARNING: Need at least 2 providers for council to work')
"
```

### 3. Test Connectivity (Optional)

If the user wants to verify API connections work:

```bash
python scripts/llm-council/council.py --query "Say hello in one word" --mode quick
```

### 4. Show Current Configuration

If config.yaml exists, summarize the configuration:

```bash
python -c "
import yaml
from pathlib import Path

config_path = Path('scripts/llm-council/config.yaml')
if config_path.exists():
    with open(config_path) as f:
        config = yaml.safe_load(f)

    council = config.get('council', {})
    members = council.get('members', [])
    chairman = council.get('chairman', {})

    print('Current Council Configuration:')
    print('=' * 40)
    print()
    print('Council Members:')
    for m in members:
        print(f'  - {m.get(\"name\", \"Unnamed\")}: {m.get(\"provider\")}/{m.get(\"model\")}')

    print()
    print(f'Chairman: {chairman.get(\"name\", \"Unnamed\")}')
    print(f'  Provider: {chairman.get(\"provider\")}')
    print(f'  Model: {chairman.get(\"model\")}')

    cost_opt = config.get('cost_optimization', {})
    print()
    print('Cost Optimization:')
    print(f'  Use fast models for review: {cost_opt.get(\"use_fast_models_for_review\", True)}')
else:
    print('No config.yaml found.')
    print('Copy config.example.yaml to config.yaml to get started.')
"
```

## Setup Instructions

If the council is not configured, provide these steps:

1. **Install dependencies**:
   ```bash
   pip install -r scripts/llm-council/requirements.txt
   ```

2. **Copy configuration template**:
   ```bash
   cp scripts/llm-council/config.example.yaml scripts/llm-council/config.yaml
   ```

3. **Set API keys** in `.env`:
   ```bash
   cp .env.example .env
   # Then edit .env and add your API keys
   ```

4. **Customize** `config.yaml` to select your preferred models

5. **Test** with a simple query:
   ```bash
   python scripts/llm-council/council.py --query "Hello, council!" --mode quick
   ```
