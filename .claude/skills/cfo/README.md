# CFO (Chief Financial Officer) Skill

> A PhD-grade financial analyst for cloud infrastructure costs, FinOps, and strategic financial planning.

---

## Overview

The CFO skill provides comprehensive financial analysis and strategic guidance for software projects, with a focus on:

- **Cloud Cost Monitoring**: Track spending across AWS, GCP, Azure, and other providers
- **Financial Analysis**: Detailed cost breakdowns, trends, and forecasts
- **Cost Optimization**: Actionable recommendations to reduce expenses
- **Revenue Strategy**: Monetization models and pricing recommendations
- **FinOps Best Practices**: Industry-standard financial operations

## Quick Start

### Invoke the CFO

```bash
# Comprehensive analysis
/cfo

# Specific analysis
/cfo analyze our AWS costs

# With billing data
/cfo analyze billing data at ./aws-june-2024.csv
```

### Run Scripts Directly

```bash
# Scan codebase for cloud services
python .claude/skills/cfo/scripts/analyze_costs.py --project-root .

# Parse billing export
python .claude/skills/cfo/scripts/parse_bills.py --file billing.csv --provider aws

# Generate forecast
python .claude/skills/cfo/scripts/forecast.py --base-cost 5000 --months 6 --growth-rate 0.10
```

## What's Included

```
.claude/skills/cfo/
├── skill.md              # Main CFO instructions (PhD-grade analysis)
├── README.md             # This file
├── EXAMPLES.md           # Real-world usage examples
├── references/           # Knowledge base
│   ├── cloud-pricing.md      # AWS, GCP, Azure pricing reference
│   ├── finops-framework.md   # FinOps Foundation best practices
│   ├── cost-categories.md    # Standard cost taxonomy
│   └── revenue-streams.md    # Monetization strategies
└── scripts/              # Deterministic cost calculations
    ├── README.md             # Scripts documentation
    ├── analyze_costs.py      # Codebase cost scanner
    ├── parse_bills.py        # Billing data parser
    └── forecast.py           # Cost forecasting tool
```

## Key Features

### 1. Code-Based Cost Discovery

Automatically scans your codebase to identify:
- Cloud SDK usage (boto3, google-cloud, azure-sdk, etc.)
- Infrastructure-as-code (Terraform, CloudFormation, Pulumi)
- Third-party service integrations
- Managed service deployments

**Supported Providers**:
- ✅ AWS (EC2, Lambda, S3, RDS, DynamoDB, etc.)
- ✅ GCP (Compute Engine, Cloud Functions, Cloud Storage, etc.)
- ✅ Azure (VMs, Functions, Blob Storage, etc.)
- ✅ Vercel, Netlify, Heroku
- ✅ Extensible for custom providers

### 2. Deterministic Cost Analysis

Unlike pure LLM estimation, the CFO skill uses Python scripts for accurate calculations:
- **No hallucination**: Math-based cost estimates
- **Reproducible**: Same input = same output
- **Auditable**: Clear calculation methodology
- **Customizable**: Adjust estimates for your negotiated rates

### 3. Comprehensive Reporting

Generate executive-ready reports:
- **Executive Summary**: High-level metrics and trends
- **Detailed Breakdown**: By provider, service, environment, team
- **Optimization Roadmap**: Prioritized by impact/effort/risk
- **Financial Forecasts**: 6-12 month projections
- **Revenue Strategy**: Monetization and pricing recommendations

### 4. FinOps Framework Alignment

Based on [FinOps Foundation](https://www.finops.org/) best practices:
- **Inform**: Visibility and allocation
- **Optimize**: Reduce waste and improve efficiency
- **Operate**: Governance and continuous improvement

### 5. Revenue Strategy Guidance

PhD-level strategic guidance on:
- Pricing models (usage-based, subscriptions, freemium, etc.)
- Revenue forecasting
- Unit economics (LTV, CAC, margins)
- Cost recovery strategies
- Competitive positioning

## Use Cases

### 1. Project Kickoff
**Question**: What will this cost to run?
**Action**: `/cfo analyze expected cloud costs`
**Output**: Baseline cost estimate before launch

### 2. Cost Spike Investigation
**Question**: Why did our bill jump?
**Action**: `/cfo analyze billing data at ./bill.csv`
**Output**: Root cause analysis with remediation

### 3. Architecture Decisions
**Question**: Lambda vs ECS - which is cheaper?
**Action**: `/cfo compare Lambda vs ECS for our workload`
**Output**: Cost comparison with recommendation

### 4. Quarterly Reviews
**Question**: How are we tracking financially?
**Action**: `/cfo quarterly financial report`
**Output**: Executive summary with trends and actions

### 5. Cost Optimization
**Question**: How do we cut costs 30%?
**Action**: `/cfo find 30% cost reduction opportunities`
**Output**: Tiered optimization roadmap

### 6. Revenue Planning
**Question**: How should we monetize?
**Action**: `/cfo revenue strategy for our API`
**Output**: Pricing recommendations and forecasts

### 7. Pre-Investment
**Question**: What are our unit economics?
**Action**: `/cfo calculate unit economics`
**Output**: Cost per user/transaction, margins, LTV

## Real-World Examples

See `EXAMPLES.md` for detailed walkthroughs:
1. Initial project cost assessment
2. Cost spike investigation
3. Architecture decision (Lambda vs ECS)
4. Quarterly financial review
5. Revenue strategy planning
6. 30% cost reduction sprint
7. Pricing change impact analysis
8. Multi-cloud comparison

## Integration Options

### 1. Interactive (Slash Command)
```
/cfo analyze our infrastructure costs
```

### 2. Programmatic (Scripts)
```bash
python scripts/analyze_costs.py --project-root . --format json > costs.json
```

### 3. CI/CD Pipeline
```yaml
# .github/workflows/cost-check.yml
- name: Analyze costs
  run: |
    python .claude/skills/cfo/scripts/analyze_costs.py \
      --project-root . \
      --output cost-report.md
```

### 4. Pre-commit Hook
```bash
# .git/hooks/pre-commit
python .claude/skills/cfo/scripts/analyze_costs.py --project-root .
# Warn if costs increased >10%
```

## Reference Materials

### Cloud Pricing (`references/cloud-pricing.md`)
- AWS, GCP, Azure pricing tables
- Regional variations
- Discount programs (RI, Savings Plans, CUD)
- Quick cost estimation formulas
- Updated: January 2025

### FinOps Framework (`references/finops-framework.md`)
- FinOps lifecycle (Inform → Optimize → Operate)
- Maturity model (Crawl → Walk → Run)
- KPIs and metrics
- Tagging strategies
- Common anti-patterns

### Cost Categories (`references/cost-categories.md`)
- Standard taxonomy (Compute, Storage, Database, etc.)
- Cost allocation models
- Industry benchmarks
- Waste identification

### Revenue Streams (`references/revenue-streams.md`)
- Monetization models (usage, subscription, freemium, etc.)
- Pricing psychology
- Revenue forecasting
- Unit economics
- Real-world examples

## Tips for Best Results

### 1. Use Actual Billing Data
**Estimates from code**: ±30% accuracy
**Actual billing data**: 100% accuracy

Provide billing exports whenever possible:
```
/cfo analyze billing data at ./aws-cost-report.csv
```

### 2. Be Specific
**Vague**: `/cfo help with costs`
**Specific**: `/cfo find Lambda optimization opportunities saving >$500/month`

### 3. Regular Reviews
- **Weekly**: Quick health check
- **Monthly**: Detailed analysis
- **Quarterly**: Strategic planning

### 4. Combine Tools
- Code scan + billing data = complete picture
- Historical trends + forecasts = budget planning
- Cost analysis + revenue strategy = profitability roadmap

### 5. Act on Recommendations
The CFO skill prioritizes recommendations by:
- **Impact**: Potential savings
- **Effort**: Implementation time
- **Risk**: Business continuity

Start with high-impact, low-effort, low-risk wins.

## Customization

### Adjust Cost Estimates

Edit `scripts/analyze_costs.py`:
```python
COST_ESTIMATES = {
    "aws": {
        "lambda": 5,  # Your negotiated rate
        "ec2": {...}
    }
}
```

### Add Cloud Providers

Add patterns to `scripts/analyze_costs.py`:
```python
CLOUD_PATTERNS = {
    "your_provider": {
        "imports": [r"import your_sdk"],
        "services": {
            "compute": [r"YourSDK\.Instance"]
        }
    }
}
```

### Custom Reports

Modify `scripts/analyze_costs.py` `format_markdown_report()` function.

## Troubleshooting

### "No services found"
- Check if cloud SDKs are actually imported in code
- Verify file extensions are scanned (`.py`, `.js`, `.ts`, etc.)
- Infrastructure might be defined outside codebase (manual entry needed)

### "Estimates seem off"
- Verify region (prices vary by region)
- Check for negotiated discounts (update `COST_ESTIMATES`)
- Consider reserved capacity if using heavily

### "Missing provider"
- Add custom provider patterns (see Customization)
- Open issue/PR to add to default patterns

## Contributing

Found a bug or want to add a feature?

1. **Bug reports**: Open an issue with examples
2. **Pricing updates**: Update `references/cloud-pricing.md`
3. **New providers**: Add to `scripts/analyze_costs.py`
4. **New use cases**: Add to `EXAMPLES.md`

## License

Part of the Claude Code Project Template.

## Credits

- **FinOps Framework**: [FinOps Foundation](https://www.finops.org/)
- **Cloud Pricing Data**: AWS, GCP, Azure official docs
- **Design Pattern**: Based on Anthropic's Skills architecture

---

**Ready to optimize your cloud costs?** Try `/cfo` now!
