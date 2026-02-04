# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.4.0] - 2025-12-16

### Added
- **PDF Semantic Decomposition Tool** - Transform large PDFs into organized markdown knowledge bases
  - `scripts/pdf-parser/` - Core parsing tool with three-phase processing:
    1. Chunk Extraction - Splits PDFs into ~2000 token chunks, extracts images
    2. Semantic Analysis - LLM reads chunks sequentially, proposes folder/file structure
    3. Content Organization - LLM writes organized markdown with images
  - `/parse-pdf` slash command for easy invocation
  - Support for Anthropic and OpenAI providers
  - Automatic semantic organization by topic
  - Image extraction with markdown embedding
  - Table extraction as markdown tables
  - Source PDF metadata in output files
- Updated `docs/references/.gitkeep` with PDF parsing instructions
- PDF parser troubleshooting in `docs/GETTING_STARTED.md`

## [1.3.0] - 2025-12-16

### Added
- **Agentic Solutions Documentation** - Comprehensive guide for building AI agents
  - `docs/AGENTIC_GUIDE.md` - Patterns for sub-agents, skills, long-running agents
  - `docs/AGENT_SDK_QUICKSTART.md` - Getting started with Claude Agent SDK
  - `/agent-plan` command for designing agentic workflows
  - `scripts/agent-examples/` - Working autonomous task agent example
  - `examples/agentic-claude-md/` - CLAUDE.md template optimized for agents
- Based on Anthropic's official patterns:
  - [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
  - [Claude Agent SDK](https://docs.anthropic.com/en/docs/claude-code/sdk)
  - [Autonomous Coding Quickstart](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)

## [1.2.0] - 2025-12-16

### Added
- Interactive initialization scripts (`init-project.sh`, `init-project.ps1`) for guided project setup
- `/health` command for diagnosing project configuration
- Example CLAUDE.md templates for common tech stacks:
  - TypeScript + React (frontend)
  - Python + FastAPI (backend)
  - Node.js + Express (backend)
- Test example files for TypeScript, Python, and JavaScript
- Expanded troubleshooting section with 14 common issues and solutions
- Performance expectations section in LLM Council guide (timing, optimization)
- This CHANGELOG file

### Fixed
- Orphaned documentation references in CLAUDE.md (api.md, schema.md)
- Clarified settings.local.json purpose (gitignored, auto-populated)

## [1.1.0] - 2025-12-15

### Added
- **LLM Council** - Multi-model advisory board for decision-making
  - BYOK (Bring Your Own Keys) architecture
  - Support for Anthropic, OpenAI, Google AI, and xAI providers
  - Three-stage deliberation: responses, peer review, chairman synthesis
  - Three consultation modes: `quick`, `full`, `vote`
  - Cost optimization with configurable fast model overrides
- `/council` slash command for consulting the council
- `/council-config` slash command for checking configuration
- Comprehensive LLM Council documentation (`docs/LLM_COUNCIL_GUIDE.md`)
- Environment variable examples for all providers (`.env.example`)

## [1.0.0] - 2025-12-14

### Added
- Initial Claude Code project template
- Core slash commands:
  - `/brainstorm` - Explore options before committing to an approach
  - `/plan` - Create implementation plan before coding
  - `/debug` - Systematic issue investigation
  - `/review` - Code review with checklist
  - `/test` - Generate comprehensive tests
  - `/refactor` - Safe, test-verified refactoring
  - `/commit` - Create well-structured commits
- CLAUDE.md template with comprehensive sections
- Best practices documentation (`docs/BEST_PRACTICES.md`)
- Getting started guide (`docs/GETTING_STARTED.md`)
- UI design guide (`docs/UI_DESIGN_GUIDE.md`)
- Skills guide for building digital employees (`docs/SKILLS_GUIDE.md`)
- Settings configuration with hooks examples
- GitHub Actions workflow example for PR reviews
- Comprehensive .gitignore

---

## Upgrade Guide

### From 1.0.0 to 1.1.0

No breaking changes. To use the new LLM Council feature:

1. Copy `scripts/llm-council/config.example.yaml` to `config.yaml`
2. Set API keys in `.env` (at least 2 providers required)
3. Install dependencies: `pip install -r scripts/llm-council/requirements.txt`
4. Use `/council <question>` to consult the council

### From 1.1.0 to 1.2.0

No breaking changes. New features are additive:

- Run `./init-project.sh` (or `.ps1` on Windows) for guided setup
- Use `/health` to check your configuration
- Check `examples/` for tech stack-specific CLAUDE.md templates

### From 1.2.0 to 1.3.0

No breaking changes. New agentic documentation is additive:

- Read `docs/AGENTIC_GUIDE.md` for building AI agents
- Use `/agent-plan` to design agentic workflows
- See `scripts/agent-examples/` for working code

### From 1.3.0 to 1.4.0

No breaking changes. New PDF parsing feature is additive:

1. Install dependencies: `pip install -r scripts/pdf-parser/requirements.txt`
2. Set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in `.env`
3. Use `/parse-pdf <path>` to transform large PDFs into organized markdown

[Unreleased]: https://github.com/brencon/claude-code-project-template/compare/v1.4.0...HEAD
[1.4.0]: https://github.com/brencon/claude-code-project-template/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/brencon/claude-code-project-template/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/brencon/claude-code-project-template/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/brencon/claude-code-project-template/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/brencon/claude-code-project-template/releases/tag/v1.0.0
