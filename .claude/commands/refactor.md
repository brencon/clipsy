# Refactor Code

Refactor the following while preserving behavior: $ARGUMENTS

## Refactoring Principles

1. **Preserve Behavior**: No functional changes unless explicitly requested
2. **Small Steps**: Make incremental changes, verify tests pass
3. **Follow Patterns**: Align with existing codebase conventions
4. **Improve Readability**: Make code more understandable
5. **Reduce Complexity**: Simplify where possible

## Scope

**Refactoring is strictly about improving existing code structure.**

Do NOT:
- Write new tests (use `/test` command separately if needed)
- Add new features or functionality
- Change behavior

Do:
- Extract duplicate code into shared functions
- Move imports to top of files
- Rename for clarity
- Reduce nesting and complexity
- Remove dead code

## Before Starting

- Run existing tests to establish baseline
- Note current coverage (for reference only, not to improve)

## Refactoring Steps

1. **Analyze**: Identify code smells and improvement opportunities
2. **Plan**: List specific changes to make
3. **Execute**: Make changes incrementally
4. **Verify**: Run tests after each change
5. **Review**: Ensure code is cleaner without behavior changes

## Common Improvements

- Extract methods for better readability
- Rename variables/functions for clarity
- Remove dead code
- Reduce nesting and complexity
- Apply appropriate design patterns
- Improve type safety
- Move imports to module level

## Output

Provide:
- Summary of changes made
- Before/after comparison for significant changes
- Confirmation that tests still pass
- Any follow-up suggestions (including potential test improvements as separate work)
