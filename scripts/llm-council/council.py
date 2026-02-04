#!/usr/bin/env python3
"""LLM Council - Multi-model deliberation system.

Consult multiple LLMs for decision-making, plan evaluation, and tie-breaking.

Based on: https://github.com/karpathy/llm-council

Usage:
    python council.py --query "Should we use REST or GraphQL?"
    python council.py --query "Evaluate this plan..." --mode full
    python council.py --query "Option A vs Option B vs Option C" --mode vote
"""

import argparse
import asyncio
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv

from providers import (
    AnthropicProvider,
    GoogleProvider,
    OpenAIProvider,
    ProviderResponse,
    XAIProvider,
)

# Load environment variables from .env file
load_dotenv()


@dataclass
class CouncilMember:
    """A member of the LLM Council."""

    provider: str
    model: str
    name: str


@dataclass
class CouncilConfig:
    """Configuration for the LLM Council."""

    members: list[CouncilMember]
    chairman: CouncilMember
    use_fast_models_for_review: bool = True
    fast_model_overrides: dict[str, str] = None
    default_mode: str = "full"
    timeout_seconds: int = 60
    max_retries: int = 2

    @classmethod
    def from_yaml(cls, path: Path) -> "CouncilConfig":
        """Load configuration from YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f)

        council_data = data.get("council", {})

        members = []
        for m in council_data.get("members", []):
            members.append(
                CouncilMember(
                    provider=m["provider"],
                    model=m["model"],
                    name=m.get("name", f"{m['provider']}/{m['model']}"),
                )
            )

        chairman_data = council_data.get("chairman", {})
        chairman = CouncilMember(
            provider=chairman_data.get("provider", "anthropic"),
            model=chairman_data.get("model", "claude-sonnet-4-20250514"),
            name=chairman_data.get("name", "Chairman"),
        )

        cost_opt = data.get("cost_optimization", {})
        defaults = data.get("defaults", {})

        return cls(
            members=members,
            chairman=chairman,
            use_fast_models_for_review=cost_opt.get("use_fast_models_for_review", True),
            fast_model_overrides=cost_opt.get("fast_model_overrides", {}),
            default_mode=defaults.get("mode", "full"),
            timeout_seconds=defaults.get("timeout_seconds", 60),
            max_retries=defaults.get("max_retries", 2),
        )

    @classmethod
    def default(cls) -> "CouncilConfig":
        """Create default configuration."""
        return cls(
            members=[
                CouncilMember("anthropic", "claude-sonnet-4-20250514", "Claude Sonnet"),
                CouncilMember("openai", "gpt-4o", "GPT-4o"),
                CouncilMember("google", "gemini-2.0-flash", "Gemini 2.0"),
            ],
            chairman=CouncilMember(
                "anthropic", "claude-sonnet-4-20250514", "Chairman (Claude)"
            ),
            fast_model_overrides={
                "anthropic": "claude-3-5-haiku-latest",
                "openai": "gpt-4o-mini",
                "google": "gemini-2.0-flash",
            },
        )


class LLMCouncil:
    """Orchestrates multi-model deliberation."""

    PROVIDERS = {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
        "google": GoogleProvider,
        "xai": XAIProvider,
    }

    def __init__(self, config: CouncilConfig):
        self.config = config
        self._providers: dict = {}

    def _get_provider(self, provider_name: str):
        """Get or create a provider instance."""
        if provider_name not in self._providers:
            provider_class = self.PROVIDERS.get(provider_name)
            if not provider_class:
                raise ValueError(f"Unknown provider: {provider_name}")
            self._providers[provider_name] = provider_class()
        return self._providers[provider_name]

    def get_available_members(self) -> list[CouncilMember]:
        """Get list of council members with available API keys."""
        available = []
        for member in self.config.members:
            provider = self._get_provider(member.provider)
            if provider.is_available():
                available.append(member)
        return available

    async def _query_member(
        self,
        member: CouncilMember,
        prompt: str,
        system_prompt: Optional[str] = None,
        use_fast_model: bool = False,
    ) -> tuple[CouncilMember, ProviderResponse]:
        """Query a single council member."""
        provider = self._get_provider(member.provider)

        model = member.model
        if use_fast_model and self.config.fast_model_overrides:
            model = self.config.fast_model_overrides.get(member.provider, model)

        response = await provider.complete(
            prompt=prompt,
            model=model,
            system_prompt=system_prompt,
        )

        return member, response

    async def stage1_gather_responses(
        self, query: str
    ) -> dict[str, tuple[CouncilMember, ProviderResponse]]:
        """Stage 1: Gather initial responses from all council members."""
        available = self.get_available_members()
        if len(available) < 2:
            raise RuntimeError(
                f"Need at least 2 council members, but only {len(available)} available. "
                "Check your API keys in .env file."
            )

        system_prompt = (
            "You are a member of an LLM Council providing your expert opinion. "
            "Be thoughtful, concise, and provide clear reasoning for your position. "
            "Focus on practical considerations and tradeoffs."
        )

        tasks = [
            self._query_member(member, query, system_prompt) for member in available
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        responses = {}
        for result in results:
            if isinstance(result, Exception):
                continue
            member, response = result
            responses[member.name] = (member, response)

        return responses

    async def stage2_peer_review(
        self,
        query: str,
        responses: dict[str, tuple[CouncilMember, ProviderResponse]],
    ) -> dict[str, dict[str, int]]:
        """Stage 2: Each member reviews and ranks others' responses."""
        rankings = {}

        # Build anonymized response summary
        response_summaries = []
        member_map = {}  # Map anonymous IDs to member names
        for i, (name, (member, response)) in enumerate(responses.items()):
            if response.success:
                anon_id = f"Response {chr(65 + i)}"  # A, B, C, etc.
                member_map[anon_id] = name
                response_summaries.append(f"### {anon_id}\n{response.content}\n")

        if len(response_summaries) < 2:
            return {}

        responses_text = "\n".join(response_summaries)

        review_prompt = f"""Original Question: {query}

The following responses were provided by different models (anonymized):

{responses_text}

Please rank these responses from best to worst based on:
1. Accuracy and correctness
2. Clarity and helpfulness
3. Practical applicability

Provide your ranking as a simple list, e.g.:
1. Response B - [brief reason]
2. Response A - [brief reason]
3. Response C - [brief reason]

Be objective and fair in your assessment."""

        system_prompt = (
            "You are reviewing responses from other AI models. "
            "Be objective and evaluate based on quality, not style preferences."
        )

        available = self.get_available_members()
        tasks = [
            self._query_member(
                member,
                review_prompt,
                system_prompt,
                use_fast_model=self.config.use_fast_models_for_review,
            )
            for member in available
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Parse rankings (simplified - could be more sophisticated)
        for result in results:
            if isinstance(result, Exception):
                continue
            member, response = result
            if response.success:
                rankings[member.name] = self._parse_rankings(
                    response.content, member_map
                )

        return rankings

    def _parse_rankings(
        self, review_text: str, member_map: dict[str, str]
    ) -> dict[str, int]:
        """Parse ranking text into scores. Higher is better."""
        scores = {}
        lines = review_text.strip().split("\n")

        rank = len(member_map)  # Start with highest score
        for line in lines:
            line = line.strip()
            for anon_id, real_name in member_map.items():
                if anon_id in line and real_name not in scores:
                    scores[real_name] = rank
                    rank -= 1
                    break

        return scores

    async def stage3_synthesize(
        self,
        query: str,
        responses: dict[str, tuple[CouncilMember, ProviderResponse]],
        rankings: Optional[dict[str, dict[str, int]]] = None,
    ) -> ProviderResponse:
        """Stage 3: Chairman synthesizes all responses into final answer."""
        # Build synthesis prompt
        response_summaries = []
        for name, (member, response) in responses.items():
            if response.success:
                response_summaries.append(f"### {name}\n{response.content}\n")

        responses_text = "\n".join(response_summaries)

        ranking_text = ""
        if rankings:
            # Calculate aggregate scores
            aggregate = {}
            for reviewer, scores in rankings.items():
                for name, score in scores.items():
                    aggregate[name] = aggregate.get(name, 0) + score

            sorted_scores = sorted(aggregate.items(), key=lambda x: x[1], reverse=True)
            ranking_text = "\n## Peer Review Rankings\n"
            for name, score in sorted_scores:
                ranking_text += f"- {name}: {score} points\n"

        synthesis_prompt = f"""Original Question: {query}

## Council Responses
{responses_text}
{ranking_text}

As the Chairman of this LLM Council, synthesize these perspectives into a comprehensive final answer. Your synthesis should:

1. Identify points of consensus among the council
2. Highlight important divergent views
3. Provide a clear, actionable recommendation
4. Note any important caveats or considerations

Be balanced and incorporate the best insights from each perspective."""

        system_prompt = (
            "You are the Chairman of an LLM Council, responsible for synthesizing "
            "multiple AI perspectives into a unified, balanced recommendation."
        )

        chairman_provider = self._get_provider(self.config.chairman.provider)
        response = await chairman_provider.complete(
            prompt=synthesis_prompt,
            model=self.config.chairman.model,
            system_prompt=system_prompt,
        )

        return response

    async def query(self, question: str, mode: str = "full") -> str:
        """Run the full council deliberation process.

        Modes:
        - quick: Just gather responses (skip peer review)
        - full: Full three-stage process
        - vote: Peer review focused on ranking/voting
        """
        output_lines = []
        output_lines.append("# LLM Council Results")
        output_lines.append("")
        output_lines.append("## Query")
        output_lines.append(f"> {question}")
        output_lines.append("")

        # Stage 1: Gather responses
        output_lines.append("## Stage 1: Individual Responses")
        output_lines.append("")

        try:
            responses = await self.stage1_gather_responses(question)
        except RuntimeError as e:
            output_lines.append(f"**Error**: {e}")
            return "\n".join(output_lines)

        for name, (member, response) in responses.items():
            output_lines.append(f"### {name}")
            if response.success:
                output_lines.append(response.content)
            else:
                output_lines.append(f"*Error: {response.error}*")
            output_lines.append("")

        rankings = None
        if mode in ("full", "vote"):
            # Stage 2: Peer review
            output_lines.append("## Stage 2: Peer Review Rankings")
            output_lines.append("")

            rankings = await self.stage2_peer_review(question, responses)

            if rankings:
                # Calculate aggregate scores
                aggregate = {}
                for reviewer, scores in rankings.items():
                    for name, score in scores.items():
                        aggregate[name] = aggregate.get(name, 0) + score

                sorted_scores = sorted(
                    aggregate.items(), key=lambda x: x[1], reverse=True
                )
                output_lines.append("| Model | Aggregate Score |")
                output_lines.append("|-------|-----------------|")
                for name, score in sorted_scores:
                    output_lines.append(f"| {name} | {score} |")
                output_lines.append("")
            else:
                output_lines.append("*Peer review could not be completed*")
                output_lines.append("")

        # Stage 3: Synthesis (except in vote-only mode)
        if mode != "vote":
            output_lines.append("## Stage 3: Chairman Synthesis")
            output_lines.append("")

            synthesis = await self.stage3_synthesize(question, responses, rankings)
            if synthesis.success:
                output_lines.append(synthesis.content)
            else:
                output_lines.append(f"*Error: {synthesis.error}*")
            output_lines.append("")

        # Summary section
        output_lines.append("---")
        output_lines.append("")
        output_lines.append(
            f"*Council consulted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        )
        output_lines.append(f"*Mode: {mode}*")
        members_list = ", ".join(
            [m.name for m in self.get_available_members()]
        )
        output_lines.append(f"*Members: {members_list}*")

        return "\n".join(output_lines)


def find_config_file() -> Optional[Path]:
    """Find the council configuration file."""
    # Check common locations
    locations = [
        Path("scripts/llm-council/config.yaml"),
        Path("config.yaml"),
        Path.home() / ".config" / "llm-council" / "config.yaml",
    ]

    for loc in locations:
        if loc.exists():
            return loc

    return None


def main():
    parser = argparse.ArgumentParser(
        description="LLM Council - Multi-model deliberation system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python council.py --query "Should we use REST or GraphQL for this API?"
  python council.py --query "Evaluate this implementation plan" --mode full
  python council.py --query "Option A vs B vs C" --mode vote
  python council.py --config ./my-config.yaml --query "..."
        """,
    )

    parser.add_argument(
        "--query",
        "-q",
        required=True,
        help="The question or decision to present to the council",
    )

    parser.add_argument(
        "--mode",
        "-m",
        choices=["quick", "full", "vote"],
        default="full",
        help="Deliberation mode: quick (responses only), full (with peer review), vote (ranking focused)",
    )

    parser.add_argument(
        "--config",
        "-c",
        type=Path,
        help="Path to configuration YAML file",
    )

    args = parser.parse_args()

    # Load configuration
    config_path = args.config or find_config_file()
    if config_path and config_path.exists():
        config = CouncilConfig.from_yaml(config_path)
    else:
        config = CouncilConfig.default()

    # Override mode if specified
    mode = args.mode or config.default_mode

    # Create council and run query
    council = LLMCouncil(config)

    # Check for available providers
    available = council.get_available_members()
    if len(available) < 2:
        print("# LLM Council Error", file=sys.stderr)
        print("", file=sys.stderr)
        print(
            f"Need at least 2 council members with API keys configured.", file=sys.stderr
        )
        print(f"Found {len(available)} available provider(s).", file=sys.stderr)
        print("", file=sys.stderr)
        print("Please set API keys in your .env file:", file=sys.stderr)
        print("  ANTHROPIC_API_KEY=...", file=sys.stderr)
        print("  OPENAI_API_KEY=...", file=sys.stderr)
        print("  GOOGLE_AI_API_KEY=...", file=sys.stderr)
        print("  XAI_API_KEY=...", file=sys.stderr)
        sys.exit(1)

    # Run the council
    result = asyncio.run(council.query(args.query, mode))
    print(result)


if __name__ == "__main__":
    main()
