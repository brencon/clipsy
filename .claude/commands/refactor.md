# Refactor Code

Refactor the following while preserving behavior: $ARGUMENTS

## Refactoring Principles

1. **Preserve Behavior**: No functional changes unless explicitly requested
2. **Small Steps**: Make incremental changes, verify tests pass
3. **Follow Patterns**: Align with existing codebase conventions
4. **Improve Readability**: Make code more understandable
5. **Reduce Complexity**: Simplify where possible
6. **DRY**: Don't Repeat Yourself - eliminate duplication

## Before Starting

- Run existing tests to establish baseline
- Check current code coverage
- If coverage is low for code being refactored, write tests first

## Refactoring Steps

1. **Analyze**: Identify code smells, duplication, and low coverage
2. **Test First**: Write tests for untested code to capture current behavior
3. **Plan**: List specific structural changes to make
4. **Execute**: Make changes incrementally
5. **Verify**: Run tests after each change
6. **Review**: Ensure code is cleaner and coverage improved

## Structural Improvements

- Extract duplicate code into shared functions (DRY)
- Introduce modularity - break large functions/classes into smaller units
- Move imports to top of files
- Rename variables/functions for clarity
- Reduce nesting and complexity
- Remove dead code
- Apply appropriate design patterns
- Improve type safety

## Test Coverage Improvements

- Add tests for any code being refactored that lacks coverage
- Ensure extracted functions have dedicated tests
- Target meaningful coverage, not just line coverage

## Output

Provide:
- Summary of structural changes made
- New tests added and coverage improvement
- Before/after comparison for significant changes
- Confirmation that all tests pass
