# Code Review

Review the specified code for quality, correctness, and best practices.

Target: $ARGUMENTS

## Review Checklist

### Correctness
- [ ] Logic is correct and handles edge cases
- [ ] Error handling is appropriate
- [ ] No potential runtime errors

### Security
- [ ] No hardcoded secrets or credentials
- [ ] Input validation where needed
- [ ] No injection vulnerabilities (SQL, XSS, command)
- [ ] Proper authentication/authorization checks

### Performance
- [ ] No unnecessary loops or computations
- [ ] Appropriate data structures used
- [ ] No memory leaks or resource issues

### Maintainability
- [ ] Code is readable and self-documenting
- [ ] Follows project conventions
- [ ] Appropriate abstractions (not over/under-engineered)
- [ ] No code duplication

### Testing
- [ ] Adequate test coverage
- [ ] Tests are meaningful (not just for coverage)
- [ ] Edge cases are tested

## Output Format

Provide:
- Summary of findings (critical, warnings, suggestions)
- Specific line references for issues
- Suggested improvements with code examples
- Overall assessment
