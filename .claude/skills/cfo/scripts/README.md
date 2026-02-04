# CFO Skill Scripts

Deterministic cost analysis and forecasting tools.

## Scripts

### analyze_costs.py

Scans codebase to identify cloud service usage and estimate costs.

**Usage:**
```bash
# Basic analysis
python analyze_costs.py --project-root /path/to/project

# Save report to file
python analyze_costs.py --project-root . --output report.md

# JSON output
python analyze_costs.py --project-root . --format json --output report.json
```

**What it does:**
- Scans code files for cloud SDK imports and API calls
- Identifies AWS, GCP, Azure, and other cloud services
- Estimates monthly costs based on service patterns
- Categorizes costs by provider, service type, and category
- Generates optimization recommendations

### parse_bills.py

Parses actual cloud billing data for detailed analysis.

**Usage:**
```bash
# Auto-detect provider
python parse_bills.py --file billing-export.csv

# Specify provider
python parse_bills.py --file aws-bill.csv --provider aws

# GCP JSON export
python parse_bills.py --file gcp-billing.json --provider gcp

# Save report
python parse_bills.py --file billing.csv --output analysis.md
```

**Supported formats:**
- AWS Cost and Usage Reports (CSV)
- GCP Billing Export (JSON)
- Azure Cost Management Export (CSV)

**What it does:**
- Parses billing exports from major cloud providers
- Aggregates costs by service, region, resource
- Identifies top cost drivers
- Calculates trends and patterns
- Finds peak usage days

### forecast.py

Projects future costs based on trends and assumptions.

**Usage:**
```bash
# Basic forecast
python forecast.py --base-cost 5000 --months 6

# With growth rate
python forecast.py --base-cost 5000 --months 12 --growth-rate 0.10

# Estimate growth from historical data
python forecast.py --base-cost 5000 --months 6 \
  --historical '[4800, 4950, 5000, 5200, 5100]'

# With seasonal factors (higher in December, lower in January)
python forecast.py --base-cost 5000 --months 12 \
  --seasonal '{"12": 1.3, "1": 0.8}'

# Save forecast
python forecast.py --base-cost 5000 --months 6 --output forecast.md
```

**What it does:**
- Projects costs with compound growth modeling
- Applies optional seasonal adjustments
- Estimates growth rate from historical data
- Calculates confidence levels
- Provides budget planning recommendations

## Requirements

```bash
pip install -r requirements.txt
```

(No external dependencies required - uses Python standard library only)

## Integration with CFO Skill

These scripts are automatically called by the CFO skill when:
- Analyzing project costs
- Processing billing data provided by user
- Generating forecasts

The CFO skill uses these scripts to ensure accurate, deterministic calculations
rather than relying on LLM estimation.

## Examples

### Complete Cost Analysis Workflow

```bash
# 1. Scan codebase for cloud services
python analyze_costs.py --project-root . --output codebase-costs.md

# 2. Parse actual billing data
python parse_bills.py --file billing-june.csv --output actual-costs.md

# 3. Compare and forecast
# Extract actual cost from billing analysis, then forecast
python forecast.py --base-cost 5234.56 --months 6 --growth-rate 0.12 \
  --output forecast-q3.md
```

### CI/CD Integration

Add to your CI pipeline to track cost-impacting changes:

```yaml
# .github/workflows/cost-check.yml
name: Cost Analysis
on: [pull_request]

jobs:
  analyze-costs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Analyze costs
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
              body: report
            });
```

## Output Formats

All scripts support both Markdown and JSON output:

**Markdown**: Human-readable reports with tables and recommendations
**JSON**: Machine-readable for integration with other tools

## Customization

### Adding Cloud Providers

Edit `analyze_costs.py` to add new providers:

```python
CLOUD_PATTERNS = {
    "your_provider": {
        "imports": [r"import your_sdk"],
        "services": {
            "service_name": [r"pattern1", r"pattern2"]
        }
    }
}

COST_ESTIMATES = {
    "your_provider": {
        "service_name": 50  # Monthly cost estimate
    }
}
```

### Adjusting Cost Estimates

Update `COST_ESTIMATES` in `analyze_costs.py` with your negotiated rates
or more accurate estimates based on your usage patterns.

## Limitations

- **Estimates are approximate**: Code-based analysis provides estimates, not exact costs
- **Usage patterns matter**: Actual costs depend on traffic, data volume, etc.
- **Pricing changes**: Provider pricing may change over time
- **Regional variations**: Costs vary by region, scripts use baseline estimates
- **Discounts not included**: Reserved instances, credits, etc. not factored in

**Always use actual billing data when available for precise analysis.**
