# Setting Up Cost Awareness Hooks

> Optional: Integrate CFO cost checks into your development workflow.

---

## Pre-Commit Hook (Cost Awareness)

The pre-commit hook alerts developers when their changes increase cloud costs.

### What It Does

- **Scans code** for cloud service usage before each commit
- **Compares** against baseline costs
- **Warns** if costs increase >10%
- **Blocks** if costs increase >50% (can override)
- **Celebrates** cost reductions

### Installation

#### Option 1: Symbolic Link (Recommended)

```bash
# From project root
ln -s ../../.claude/skills/cfo/scripts/pre-commit-cost-check.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Pros**: Auto-updates when script changes
**Cons**: Requires relative path support

#### Option 2: Copy Script

```bash
# From project root
cp .claude/skills/cfo/scripts/pre-commit-cost-check.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Pros**: Works everywhere
**Cons**: Need to manually update when script changes

#### Option 3: Using pre-commit Framework

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: cfo-cost-check
        name: CFO Cost Awareness Check
        entry: .claude/skills/cfo/scripts/pre-commit-cost-check.sh
        language: script
        pass_filenames: false
```

Then run:
```bash
pre-commit install
```

### Usage

#### Normal Commits

```bash
git add .
git commit -m "Add new feature"

# Output:
# 🔍 Running CFO cost awareness check...
# 💰 Cost Impact Analysis:
#    Previous: $247.50/month
#    Current:  $272.00/month
#    Change:   $24.50/month (9.9%)
#
# ✓ Cost impact: Minimal (9.9%)
```

#### When Costs Increase Significantly

```bash
git commit -m "Add BigQuery integration"

# Output:
# 🔍 Running CFO cost awareness check...
# 💰 Cost Impact Analysis:
#    Previous: $247.50/month
#    Current:  $347.50/month
#    Change:   $100.00/month (40.4%)
#
# ⚠️  WARNING: Costs increased by 40.4% (+$100.00/month)
#
# New services detected:
#   - GCP: bigquery
#
# Run '/cfo' for detailed analysis and optimization recommendations.
#
# Proceed with commit? (y/N)
```

#### Bypass Hook (When Needed)

```bash
# Skip hook for this commit
git commit --no-verify -m "Emergency fix"
```

### Configuration

#### Adjust Thresholds

Edit `.claude/skills/cfo/scripts/pre-commit-cost-check.sh`:

```bash
# Default thresholds
WARN_THRESHOLD=10  # Warn if >10% increase
BLOCK_THRESHOLD=50 # Block if >50% increase

# More strict
WARN_THRESHOLD=5
BLOCK_THRESHOLD=25

# More lenient
WARN_THRESHOLD=20
BLOCK_THRESHOLD=100
```

#### Reset Baseline

```bash
# Remove baseline to start fresh
rm .cfo-baseline-costs.json

# Next commit will create new baseline
git commit -m "Reset cost baseline"
```

### Baseline File

The hook creates `.cfo-baseline-costs.json` to track cost changes.

**Should you commit it?**

**Yes, if:**
- Team wants shared cost baseline
- Want to track cost evolution over time
- CI/CD should use same baseline

**No, if:**
- Each developer should have their own baseline
- Baseline contains sensitive information
- Want fresh baseline per branch

**To gitignore**:
```bash
echo ".cfo-baseline-costs.json" >> .gitignore
```

---

## CI/CD Integration

### GitHub Actions

Add to `.github/workflows/cost-check.yml`:

```yaml
name: Cost Analysis

on:
  pull_request:
    branches: [main]

jobs:
  cost-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Run cost analysis
        id: cost-analysis
        run: |
          python .claude/skills/cfo/scripts/analyze_costs.py \
            --project-root . \
            --output cost-report.md

      - name: Comment PR
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('cost-report.md', 'utf8');

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## 💰 Cloud Cost Analysis\n\n${report}`
            });

      - name: Check cost threshold
        run: |
          CURRENT_COST=$(python -c "import json; print(json.load(open('cost-report.json'))['total_estimated_cost'])")
          THRESHOLD=1000

          if (( $(echo "$CURRENT_COST > $THRESHOLD" | bc -l) )); then
            echo "::error::Monthly costs ($CURRENT_COST) exceed threshold ($THRESHOLD)"
            exit 1
          fi
```

### GitLab CI

Add to `.gitlab-ci.yml`:

```yaml
cost-check:
  stage: test
  script:
    - python .claude/skills/cfo/scripts/analyze_costs.py --project-root . --output cost-report.md
    - cat cost-report.md
  artifacts:
    reports:
      markdown: cost-report.md
  only:
    - merge_requests
```

### Bitbucket Pipelines

Add to `bitbucket-pipelines.yml`:

```yaml
pipelines:
  pull-requests:
    '**':
      - step:
          name: Cost Analysis
          script:
            - python .claude/skills/cfo/scripts/analyze_costs.py --project-root . --output cost-report.md
            - cat cost-report.md
          artifacts:
            - cost-report.md
```

---

## Post-Commit Hook (Optional)

Track cost changes over time.

### Create `.git/hooks/post-commit`:

```bash
#!/bin/bash
# Post-commit: Log cost snapshot

SCRIPT_DIR="$(git rev-parse --show-toplevel)/.claude/skills/cfo/scripts"
COST_LOG="$(git rev-parse --show-toplevel)/.cfo-cost-history.jsonl"

# Run analysis
python3 "$SCRIPT_DIR/analyze_costs.py" \
    --project-root "$(git rev-parse --show-toplevel)" \
    --format json \
    --output /tmp/cfo-snapshot.json 2>/dev/null || exit 0

# Append to log with timestamp and commit hash
python3 -c "
import json
from datetime import datetime

with open('/tmp/cfo-snapshot.json') as f:
    data = json.load(f)

snapshot = {
    'timestamp': datetime.utcnow().isoformat(),
    'commit': '$(git rev-parse HEAD)',
    'cost': data['total_estimated_cost'],
    'services': len(data['services'])
}

with open('$COST_LOG', 'a') as f:
    f.write(json.dumps(snapshot) + '\n')
"

echo "💰 Cost snapshot logged"
```

**Make executable**:
```bash
chmod +x .git/hooks/post-commit
```

**View history**:
```bash
cat .cfo-cost-history.jsonl | python -m json.tool
```

---

## Push Hook (Optional)

Warn before pushing commits that increased costs.

### Create `.git/hooks/pre-push`:

```bash
#!/bin/bash
# Pre-push: Summary of cost changes since last push

echo "🔍 Checking cost changes since last push..."

# Get commits since last push
COMMITS=$(git log @{u}.. --oneline 2>/dev/null || git log --oneline -5)

if [ -z "$COMMITS" ]; then
    echo "✓ No new commits to push"
    exit 0
fi

echo "Commits to push:"
echo "$COMMITS"
echo ""

# Check if costs changed
if [ -f .cfo-cost-history.jsonl ]; then
    FIRST_COST=$(head -1 .cfo-cost-history.jsonl | python3 -c "import sys,json; print(json.load(sys.stdin)['cost'])")
    LAST_COST=$(tail -1 .cfo-cost-history.jsonl | python3 -c "import sys,json; print(json.load(sys.stdin)['cost'])")

    CHANGE=$(python3 -c "print(round(($LAST_COST - $FIRST_COST) / $FIRST_COST * 100, 1) if $FIRST_COST > 0 else 0)")

    echo "Cost change: $CHANGE%"

    if (( $(echo "$CHANGE > 20" | bc -l) )); then
        echo "⚠️  Significant cost increase detected"
        read -p "Continue with push? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

exit 0
```

**Make executable**:
```bash
chmod +x .git/hooks/pre-push
```

---

## Troubleshooting

### Hook Not Running

**Check if executable**:
```bash
ls -la .git/hooks/pre-commit
# Should show: -rwxr-xr-x
```

**Make executable**:
```bash
chmod +x .git/hooks/pre-commit
```

### Python Not Found

**Update shebang** in hook script:
```bash
#!/usr/bin/env python3  # Try this
# or
#!/usr/bin/python3
# or
#!/usr/local/bin/python3
```

### Hook Too Slow

**Disable for large repos**:
```bash
# Skip patterns in analyze_costs.py
skip_dirs = {'.git', 'node_modules', 'venv', '.venv', 'build', 'dist', 'vendor'}
```

**Or disable**:
```bash
mv .git/hooks/pre-commit .git/hooks/pre-commit.disabled
```

### False Positives

**Adjust thresholds** or **update baseline**:
```bash
rm .cfo-baseline-costs.json
git commit -m "Update cost baseline"
```

---

## Best Practices

### 1. Start Lenient

```bash
# Week 1: High thresholds, just observe
WARN_THRESHOLD=50
BLOCK_THRESHOLD=200

# Week 2-4: Medium thresholds
WARN_THRESHOLD=25
BLOCK_THRESHOLD=100

# Production: Strict thresholds
WARN_THRESHOLD=10
BLOCK_THRESHOLD=50
```

### 2. Educate Team

Share this doc and explain:
- Why cost awareness matters
- How to interpret warnings
- When to override (rarely)

### 3. Review Regularly

```bash
# Weekly: Check cost trends
cat .cfo-cost-history.jsonl | tail -20

# Monthly: Full analysis
/cfo comprehensive cost review
```

### 4. Celebrate Wins

```bash
# When costs decrease, recognize it!
git log --grep="cost" --oneline
```

### 5. Integrate with Reviews

```bash
# In PR template
## Cost Impact
- [ ] Ran `/cfo` to check cost impact
- [ ] Costs increased by: X%
- [ ] Justification: [why increase is acceptable]
```

---

## Uninstall

Remove hooks:
```bash
rm .git/hooks/pre-commit
rm .git/hooks/post-commit
rm .git/hooks/pre-push
rm .cfo-baseline-costs.json
rm .cfo-cost-history.jsonl
```

---

**Ready to set up?** Start with the pre-commit hook and adjust thresholds as needed!
