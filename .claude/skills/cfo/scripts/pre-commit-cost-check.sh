#!/bin/bash
# Pre-commit Hook: Cost Awareness Check
#
# This hook runs before each commit to alert developers of potential cost increases.
# Install: ln -s ../../.claude/skills/cfo/scripts/pre-commit-cost-check.sh .git/hooks/pre-commit
#
# Usage:
#   - Automatic on every commit
#   - Skip with: git commit --no-verify
#

set -e

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "🔍 Running CFO cost awareness check..."

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(git rev-parse --show-toplevel)"

# Temporary files
CURRENT_COSTS="/tmp/cfo-current-costs.json"
PREVIOUS_COSTS="/tmp/cfo-previous-costs.json"

# Run cost analysis on current state
python3 "$SCRIPT_DIR/analyze_costs.py" \
    --project-root "$PROJECT_ROOT" \
    --format json \
    --output "$CURRENT_COSTS" \
    2>/dev/null || {
        echo -e "${YELLOW}⚠️  Warning: Cost analysis failed. Skipping check.${NC}"
        exit 0
    }

# Get current total cost
CURRENT_TOTAL=$(python3 -c "import json; print(json.load(open('$CURRENT_COSTS'))['total_estimated_cost'])")

# Try to get baseline costs (from last commit or baseline file)
BASELINE_FILE="$PROJECT_ROOT/.cfo-baseline-costs.json"

if [ -f "$BASELINE_FILE" ]; then
    PREVIOUS_TOTAL=$(python3 -c "import json; print(json.load(open('$BASELINE_FILE'))['total_estimated_cost'])")
else
    # No baseline exists - create one
    echo -e "${GREEN}✓ Creating baseline cost snapshot${NC}"
    cp "$CURRENT_COSTS" "$BASELINE_FILE"
    exit 0
fi

# Calculate change
CHANGE=$(python3 -c "print(round(($CURRENT_TOTAL - $PREVIOUS_TOTAL) / $PREVIOUS_TOTAL * 100, 1) if $PREVIOUS_TOTAL > 0 else 0)")
ABS_CHANGE=$(python3 -c "print(abs($CURRENT_TOTAL - $PREVIOUS_TOTAL))")

# Thresholds
WARN_THRESHOLD=10  # Warn if costs increase >10%
BLOCK_THRESHOLD=50 # Block if costs increase >50%

echo ""
echo "💰 Cost Impact Analysis:"
echo "   Previous: \$$PREVIOUS_TOTAL/month"
echo "   Current:  \$$CURRENT_TOTAL/month"
echo "   Change:   \$$ABS_CHANGE/month ($CHANGE%)"
echo ""

# Check if costs increased significantly
if (( $(echo "$CHANGE > $BLOCK_THRESHOLD" | bc -l) )); then
    echo -e "${RED}❌ COMMIT BLOCKED: Costs increased by $CHANGE% (>\$${ABS_CHANGE}/month)${NC}"
    echo ""
    echo "This commit would significantly increase cloud costs."
    echo "Please review the changes and consider cost optimization."
    echo ""
    echo "To see details, run:"
    echo "  python3 .claude/skills/cfo/scripts/analyze_costs.py --project-root ."
    echo ""
    echo "To commit anyway (not recommended):"
    echo "  git commit --no-verify"
    echo ""
    exit 1

elif (( $(echo "$CHANGE > $WARN_THRESHOLD" | bc -l) )); then
    echo -e "${YELLOW}⚠️  WARNING: Costs increased by $CHANGE% (+\$${ABS_CHANGE}/month)${NC}"
    echo ""
    echo "New cloud services or resources detected."
    echo "Consider:"
    echo "  - Are these resources necessary?"
    echo "  - Can they be optimized?"
    echo "  - Are there cheaper alternatives?"
    echo ""

    # Show what changed
    echo "New services detected:"
    python3 -c "
import json
current = json.load(open('$CURRENT_COSTS'))
previous = json.load(open('$BASELINE_FILE'))

current_services = {(s['provider'], s['service']) for s in current['services']}
previous_services = {(s['provider'], s['service']) for s in previous['services']}

new_services = current_services - previous_services
for provider, service in new_services:
    print(f'  - {provider}: {service}')
    "
    echo ""
    echo "Run '/cfo' for detailed analysis and optimization recommendations."
    echo ""

    # Ask for confirmation
    read -p "Proceed with commit? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Commit aborted.${NC}"
        exit 1
    fi

    # Update baseline
    cp "$CURRENT_COSTS" "$BASELINE_FILE"
    echo -e "${GREEN}✓ Cost baseline updated${NC}"

elif (( $(echo "$CHANGE < -$WARN_THRESHOLD" | bc -l) )); then
    echo -e "${GREEN}✓ Great! Costs decreased by ${CHANGE#-}% (-\$${ABS_CHANGE}/month)${NC}"
    echo "  Keep up the good work on cost optimization!"

    # Update baseline
    cp "$CURRENT_COSTS" "$BASELINE_FILE"

else
    echo -e "${GREEN}✓ Cost impact: Minimal ($CHANGE%)${NC}"

    # Update baseline for significant changes
    if (( $(echo "$CHANGE != 0" | bc -l) )); then
        cp "$CURRENT_COSTS" "$BASELINE_FILE"
    fi
fi

echo ""
exit 0
