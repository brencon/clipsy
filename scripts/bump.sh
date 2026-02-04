#!/bin/bash
set -e

# Usage: ./scripts/bump.sh [patch|minor|major]
# Bumps version, updates all files, commits, tags, pushes, and creates GitHub release

BUMP_TYPE="${1:-patch}"

if [[ ! "$BUMP_TYPE" =~ ^(patch|minor|major)$ ]]; then
    echo "Usage: $0 [patch|minor|major]"
    exit 1
fi

# Get current version from __init__.py
CURRENT=$(grep -o '__version__ = "[^"]*"' src/clipsy/__init__.py | cut -d'"' -f2)
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT"

# Calculate new version
case "$BUMP_TYPE" in
    patch) PATCH=$((PATCH + 1)) ;;
    minor) MINOR=$((MINOR + 1)); PATCH=0 ;;
    major) MAJOR=$((MAJOR + 1)); MINOR=0; PATCH=0 ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"

echo "Bumping version: $CURRENT → $NEW_VERSION ($BUMP_TYPE)"

# Update version in all files
sed -i '' "s/__version__ = \"$CURRENT\"/__version__ = \"$NEW_VERSION\"/" src/clipsy/__init__.py
sed -i '' "s/version = \"$CURRENT\"/version = \"$NEW_VERSION\"/" pyproject.toml
sed -i '' "s/version-$CURRENT-blue/version-$NEW_VERSION-blue/" README.md

# Run tests to make sure everything works
echo "Running tests..."
.venv/bin/python -m pytest tests/ -q

# Get test count for README badge
TEST_COUNT=$(.venv/bin/python -m pytest tests/ --collect-only -q 2>/dev/null | tail -1 | grep -o '^[0-9]*')
if [[ -n "$TEST_COUNT" ]]; then
    # Update test badge (handle both old and new counts)
    sed -i '' -E "s/tests-[0-9]+%20passed/tests-${TEST_COUNT}%20passed/" README.md
fi

# Commit and tag
git add src/clipsy/__init__.py pyproject.toml README.md
git commit -m "chore: bump version to $NEW_VERSION"
git tag "v$NEW_VERSION"

echo ""
echo "Version bumped to $NEW_VERSION"
echo ""
echo "Next steps:"
echo "  git push && git push --tags"
echo "  gh release create v$NEW_VERSION --title \"Clipsy v$NEW_VERSION\" --generate-notes"
echo ""
echo "Or run with --push to do it automatically:"
echo "  $0 $BUMP_TYPE --push"

# Auto-push if requested
if [[ "$2" == "--push" ]]; then
    echo ""
    echo "Pushing to remote..."
    git push && git push --tags

    echo "Creating GitHub release..."
    gh release create "v$NEW_VERSION" --title "Clipsy v$NEW_VERSION" --generate-notes

    echo ""
    echo "Done! Release: https://github.com/brencon/clipsy/releases/tag/v$NEW_VERSION"
fi
