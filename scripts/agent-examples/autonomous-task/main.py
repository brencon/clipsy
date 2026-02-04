#!/usr/bin/env python3
"""
Autonomous Task Agent - Main Entry Point

A long-running agent implementation based on Anthropic's two-agent pattern.
See: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents

Usage:
    # First run - initialize with a task
    python main.py --task "Implement a REST API for user management"

    # Subsequent runs - continue from saved state
    python main.py

    # Force re-initialization
    python main.py --task "New task" --force
"""

import argparse
import asyncio
import os
import subprocess
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

from progress import ProgressTracker, FeatureList, create_initial_feature_list
from security import SecurityValidator, create_validator_from_config


# Load environment variables
load_dotenv()


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    config_file = Path(config_path)

    if not config_file.exists():
        # Use example config as default
        example_config = Path("config.example.yaml")
        if example_config.exists():
            print(f"Note: Using {example_config} (copy to {config_path} to customize)")
            config_file = example_config
        else:
            return {}

    with open(config_file) as f:
        return yaml.safe_load(f) or {}


def read_prompt(prompt_name: str) -> str:
    """Read a prompt template from the prompts directory."""
    prompt_path = Path("prompts") / f"{prompt_name}.md"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt not found: {prompt_path}")
    return prompt_path.read_text()


def run_tests() -> tuple[bool, str]:
    """Run the project's test suite."""
    test_commands = [
        "npm test",
        "pytest",
        "python -m pytest",
        "go test ./...",
        "cargo test",
    ]

    for cmd in test_commands:
        try:
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                return True, result.stdout
            # If command exists but tests fail, return the failure
            if "not found" not in result.stderr.lower():
                return False, result.stdout + result.stderr
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue

    return True, "No test suite detected"


def git_checkpoint(message: str) -> bool:
    """Create a git checkpoint commit."""
    try:
        # Stage all changes
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)

        # Check if there are changes to commit
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True
        )
        if not result.stdout.strip():
            return True  # Nothing to commit

        # Commit
        subprocess.run(
            ["git", "commit", "-m", message],
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


async def run_initializer_agent(task: str, tracker: ProgressTracker) -> None:
    """Run the initializer agent for first-time setup."""
    print("\n=== Running Initializer Agent ===\n")

    tracker.log_section("Task Initialization")
    tracker.log_progress(f"Task: {task}")

    # Read the initializer prompt
    try:
        prompt_template = read_prompt("initializer")
    except FileNotFoundError:
        prompt_template = """You are initializing a new autonomous coding task.

Task: {task}

Your job is to:
1. Analyze the requirements
2. Break them down into features
3. Create a feature list
4. Start implementing the first feature

Output a JSON feature list in this format:
{{
  "features": [
    {{"name": "Feature 1", "description": "Description"}},
    ...
  ]
}}

Then begin implementing the first feature."""

    prompt = prompt_template.format(task=task)

    # In a real implementation, this would call the Claude API
    # For now, we'll create a placeholder feature list
    print(f"Task: {task}")
    print("\nIn production, this would call Claude to:")
    print("  1. Analyze the requirements")
    print("  2. Create a feature breakdown")
    print("  3. Begin implementation")
    print("\nFor now, creating a placeholder feature list...")

    # Create placeholder features (in production, Claude would generate these)
    placeholder_features = [
        {"name": "Core setup", "description": "Set up project structure"},
        {"name": "Main functionality", "description": "Implement core features"},
        {"name": "Tests", "description": "Add test coverage"},
        {"name": "Documentation", "description": "Add documentation"},
    ]

    feature_list = create_initial_feature_list(task, placeholder_features)
    tracker.save_feature_list(feature_list)

    tracker.log_progress(f"Created {len(feature_list.features)} features")
    print(f"\nCreated feature list with {len(feature_list.features)} features")
    print("Run again to continue with the worker agent")


async def run_worker_agent(tracker: ProgressTracker, validator: SecurityValidator) -> None:
    """Run the worker agent to continue implementation."""
    print("\n=== Running Worker Agent ===\n")

    # Load existing state
    feature_list = tracker.load_feature_list()
    if not feature_list:
        print("Error: No feature list found. Run with --task to initialize.")
        return

    # Show current progress
    print(tracker.get_summary())

    # Check if complete
    if feature_list.is_complete():
        print("\n All features complete!")
        return

    # Run tests first
    print("Running tests to verify state...")
    tests_pass, test_output = run_tests()

    if not tests_pass:
        print("Tests failing! Prioritizing bug fixes...")
        tracker.log_progress("Tests failing - prioritizing fixes")
        # In production, Claude would analyze and fix

    # Get next feature
    next_feature = feature_list.get_next_pending()
    if not next_feature:
        in_progress = feature_list.get_in_progress()
        if in_progress:
            next_feature = in_progress[0]
            print(f"Resuming in-progress feature: {next_feature.name}")
        else:
            print("No pending features and none in progress")
            return

    print(f"\nWorking on: {next_feature.name}")
    print(f"Description: {next_feature.description}")

    tracker.mark_feature_started(next_feature.id)

    # Read the worker prompt
    try:
        prompt_template = read_prompt("worker")
    except FileNotFoundError:
        prompt_template = """You are continuing work on an autonomous coding task.

Current feature: {feature_name}
Description: {feature_description}

Previous progress:
{progress}

Continue implementing this feature. When complete, move to the next one."""

    prompt = prompt_template.format(
        feature_name=next_feature.name,
        feature_description=next_feature.description,
        progress=tracker.read_progress()[-2000:],  # Last 2000 chars
    )

    # In production, this would call Claude
    print("\nIn production, Claude would now:")
    print(f"  1. Implement '{next_feature.name}'")
    print("  2. Write tests")
    print("  3. Verify with existing tests")
    print("  4. Commit changes")

    # Simulate completion for demo
    print("\n(Demo: marking feature as complete)")
    tracker.mark_feature_complete(next_feature.id)

    # Checkpoint
    commit_msg = f"feat(agent): {next_feature.name}"
    if git_checkpoint(commit_msg):
        tracker.log_progress(f"Checkpoint: {commit_msg}")

    print("\n" + tracker.get_summary())


async def main():
    parser = argparse.ArgumentParser(description="Autonomous Task Agent")
    parser.add_argument(
        "--task",
        type=str,
        help="Task description (required for first run)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-initialization even if state exists"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to config file"
    )

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Initialize components
    state_config = config.get("state", {})
    tracker = ProgressTracker(
        progress_file=state_config.get("progress_file", "progress.txt"),
        feature_file=state_config.get("feature_file", "feature_list.json"),
    )
    validator = create_validator_from_config(config)

    # Determine which agent to run
    if args.force or not tracker.has_existing_state():
        if not args.task:
            print("Error: --task required for initial run")
            print("Usage: python main.py --task 'Your task description'")
            sys.exit(1)
        await run_initializer_agent(args.task, tracker)
    else:
        await run_worker_agent(tracker, validator)


if __name__ == "__main__":
    asyncio.run(main())
