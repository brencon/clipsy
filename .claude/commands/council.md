# LLM Council Consultation

Consult the LLM Council for expert input on: $ARGUMENTS

## Overview

The LLM Council is an "agentic advisory board" that queries multiple AI models to provide diverse perspectives on decisions, plans, and tradeoffs.

## Instructions

1. **Check if council is configured**: Look for `scripts/llm-council/config.yaml` and verify API keys are set in `.env`

2. **If not configured**, inform the user:
   - They need to copy `config.example.yaml` to `config.yaml`
   - They need to set API keys in `.env` (at least 2 providers)
   - Run `pip install -r scripts/llm-council/requirements.txt`

3. **If configured**, execute the council:
   ```bash
   python scripts/llm-council/council.py --query "$ARGUMENTS" --mode full
   ```

4. **Present the results** to the user with clear formatting

5. **Add your analysis**: After showing council results, provide your own synthesis:
   - Do you agree with the chairman's synthesis?
   - Are there additional considerations specific to this codebase?
   - What's your recommendation given the full context?

## Modes

Choose the appropriate mode based on the query:

- `--mode quick`: Fast responses only (skip peer review). Use for simple questions.
- `--mode full`: Complete deliberation with peer review. Use for important decisions.
- `--mode vote`: Focus on ranking options. Use for "A vs B vs C" questions.

## Example Queries

- Architecture decisions: "Should we use REST or GraphQL for the API?"
- Technology choices: "PostgreSQL vs MongoDB for our data model?"
- Implementation approaches: "Microservices vs monolith for this feature?"
- Plan evaluation: "Review this implementation plan: [plan details]"
- Tie-breaking: "Option A [details] vs Option B [details]"

## Important

- The council provides external perspectives, but YOU have the codebase context
- Always consider the council's input alongside your understanding of the project
- For highly project-specific decisions, your analysis may outweigh council consensus
