# Test Examples

This directory contains example test patterns for different tech stacks. Use these as references when writing tests in your project.

## Available Examples

| File | Tech Stack | Testing Framework |
|------|------------|-------------------|
| [example.test.ts](example.test.ts) | TypeScript | Vitest/Jest |
| [example_test.py](example_test.py) | Python | pytest |
| [example.test.js](example.test.js) | Node.js | Jest |

## Test Conventions

### File Naming
- **TypeScript/JavaScript**: `*.test.ts`, `*.test.js`, or `*.spec.ts`
- **Python**: `test_*.py` or `*_test.py`

### Test Structure
All examples follow the AAA pattern:
1. **Arrange**: Set up test data and conditions
2. **Act**: Execute the code being tested
3. **Assert**: Verify the expected outcome

### What to Test
- **Unit tests**: Individual functions and methods
- **Integration tests**: Component interactions
- **Edge cases**: Null, empty, boundary values
- **Error handling**: Expected exceptions and failures

## Running Tests

### TypeScript/JavaScript
```bash
# Vitest
npm test
npx vitest run

# Jest
npm test
npx jest
```

### Python
```bash
# pytest
pytest
pytest tests/
pytest -v  # verbose
pytest --cov=src  # with coverage
```

## Writing Good Tests

1. **Test behavior, not implementation** - Tests should verify what code does, not how it does it
2. **One assertion per concept** - Each test should verify one thing
3. **Descriptive names** - Test names should explain what's being tested
4. **Independent tests** - Tests shouldn't depend on each other
5. **Fast tests** - Unit tests should run in milliseconds

## Customizing for Your Project

1. Delete examples for tech stacks you don't use
2. Add your actual test files alongside or instead of examples
3. Update test configuration in `package.json`, `pytest.ini`, etc.
4. Configure CI/CD to run tests on PRs
