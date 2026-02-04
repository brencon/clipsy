# CFO - Chief Financial Officer Analysis

Invoke the CFO skill for comprehensive financial analysis of cloud costs and revenue strategy.

## What This Does

Activates the CFO skill to act as your Chief Financial Officer, providing:
- Cloud cost discovery and analysis
- Financial reporting and forecasting
- Cost optimization recommendations
- Revenue strategy suggestions
- FinOps best practices

## Usage

```
/cfo [optional: specific analysis request]
```

## Examples

```
/cfo
→ Comprehensive financial analysis of the project

/cfo analyze our AWS costs
→ Focus on AWS cost breakdown

/cfo forecast next 6 months
→ Generate cost forecast

/cfo revenue strategy
→ Recommend revenue streams to offset costs

/cfo optimize compute costs
→ Find compute optimization opportunities
```

## What the CFO Will Do

When invoked, the CFO skill will:

1. **Discover Cloud Services**
   - Scan codebase for cloud SDK usage (AWS, GCP, Azure, etc.)
   - Identify infrastructure-as-code configurations
   - Find third-party service integrations

2. **Analyze Costs**
   - Run deterministic cost calculations using scripts
   - Categorize costs by provider, service, environment
   - Identify trends and anomalies
   - Compare against industry benchmarks

3. **Generate Recommendations**
   - Quick wins (immediate savings)
   - Strategic optimizations (medium-term)
   - Architectural improvements (long-term)
   - Prioritize by impact/effort/risk

4. **Revenue Strategy**
   - Analyze current revenue (if applicable)
   - Recommend monetization models
   - Calculate unit economics
   - Suggest pricing strategies

5. **Create Reports**
   - Executive summary
   - Detailed cost breakdown
   - Optimization opportunities
   - Forecasts and budgets
   - Action items

## When to Use

Invoke the CFO when:
- Starting a new project (baseline costs)
- Before major infrastructure changes
- Investigating cost spikes
- Planning budgets
- Considering pricing changes
- Quarterly financial reviews
- Preparing for funding/board meetings

## Optional: Provide Billing Data

For more accurate analysis, you can provide actual billing data:

```
/cfo analyze billing data at ./billing-june-2024.csv
```

Supported formats:
- AWS Cost and Usage Reports (CSV)
- GCP Billing Export (JSON)
- Azure Cost Management Export (CSV)

## Related Documentation

- CFO Skill: `.claude/skills/cfo/skill.md`
- Cloud Pricing: `.claude/skills/cfo/references/cloud-pricing.md`
- FinOps Framework: `.claude/skills/cfo/references/finops-framework.md`
- Revenue Models: `.claude/skills/cfo/references/revenue-streams.md`

---

**Note**: The CFO skill provides estimates based on code analysis. For precise cost tracking, use actual billing data from your cloud providers.

---

## Arguments

$ARGUMENTS will be passed to the CFO skill as the specific analysis request. If empty, performs comprehensive analysis.
