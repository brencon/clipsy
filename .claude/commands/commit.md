# Create Commit

Create a well-structured commit for the current changes.

## Process

1. Run `git status` to see all changes
2. Run `git diff` to review what changed
3. Run `git log -5 --oneline` to see recent commit style
4. Group related changes logically
5. Write a clear commit message

## Commit Message Format

Follow conventional commits:

```
<type>(<scope>): <short description>

<body - explain WHY, not WHAT>

<footer - breaking changes, issue refs>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, no code change
- `refactor`: Code change that neither fixes nor adds
- `test`: Adding or updating tests
- `chore`: Build process, dependencies, etc.

## Guidelines

- First line: 50 chars max, imperative mood
- Body: Wrap at 72 chars, explain motivation
- Reference issues: `Fixes #123` or `Relates to #456`
- Do NOT commit: `.env`, credentials, `node_modules`, build artifacts

## Additional Instructions

$ARGUMENTS
