# CFO Skill - Usage Examples

> Real-world examples of using the CFO skill for cloud cost analysis and financial planning.

---

## Example 1: Initial Project Cost Assessment

### Scenario
New project starting, need to understand baseline cloud costs before launch.

### Invocation
```
/cfo analyze expected cloud costs for this project
```

### What Happens

1. **Code Scan**
   - Searches for AWS SDK imports in Python files
   - Finds: Lambda functions, DynamoDB tables, S3 buckets
   - Identifies API Gateway configuration

2. **Cost Estimation**
   - Runs `analyze_costs.py` script
   - Estimates based on code patterns
   - Categorizes by service type

3. **Report Generated**
   ```markdown
   # CFO Financial Analysis Report
   **Project**: MyApp API
   **Total Estimated Monthly Cost**: $247.50

   ## Identified Services
   | Provider | Service | Est. Cost |
   |----------|---------|-----------|
   | AWS | Lambda | $45.00 |
   | AWS | DynamoDB | $75.00 |
   | AWS | S3 | $25.00 |
   | AWS | API Gateway | $50.00 |
   | AWS | CloudWatch | $30.00 |
   | Vercel | Hosting | $20.00 |

   ## Quick Wins
   1. Use S3 Intelligent-Tiering (save ~$8/mo)
   2. Implement Lambda provisioned concurrency strategically
   3. Set up CloudWatch log retention policies (save ~$5/mo)
   ```

### Outcome
- Clear baseline: ~$250/month
- Identified $13/month in quick savings
- Informed budget planning

---

## Example 2: Cost Spike Investigation

### Scenario
AWS bill jumped from $500 to $1,200 last month. Need to find the cause.

### Invocation
```
/cfo analyze billing data at ./aws-bill-june.csv
```

### What Happens

1. **Parse Billing Data**
   - Runs `parse_bills.py --file aws-bill-june.csv`
   - Extracts detailed line items
   - Identifies anomalies

2. **Trend Analysis**
   - Compares to historical patterns
   - Calculates month-over-month change
   - Identifies peak days

3. **Report Generated**
   ```markdown
   # Billing Analysis - June 2024

   **Total Cost**: $1,247.89 (+149% vs May)

   ## Top Cost Drivers (by change)
   1. **Data Transfer OUT**: $687 (+$612 vs May) ⚠️
   2. **RDS db.m5.large**: $234 (+$84 vs May)
   3. **EC2 c5.2xlarge**: $198 (unchanged)

   ## Anomaly Detected
   - June 15-17: Data transfer spike (847 GB/day vs avg 45 GB/day)
   - Recommendation: Investigate application behavior on those dates
   - Likely cause: Large dataset export or misconfigured sync

   ## Immediate Actions
   - [ ] Review CloudWatch metrics for June 15-17
   - [ ] Check for unintended data replication
   - [ ] Implement CloudFront CDN (save ~$200/mo ongoing)
   ```

### Outcome
- Identified root cause (data transfer spike)
- Found ongoing optimization ($200/month)
- Prevented future overages

---

## Example 3: Pre-Architecture Decision

### Scenario
Deciding between serverless (Lambda) vs containers (ECS) for new service.

### Invocation
```
/cfo compare costs: AWS Lambda vs ECS Fargate for API service with 10M requests/month
```

### What Happens

1. **Cost Modeling**
   - Calculates Lambda costs (invocations + duration)
   - Calculates Fargate costs (vCPU + memory hours)
   - Considers scaling patterns

2. **Comparison Analysis**
   ```markdown
   # Architecture Cost Comparison

   ## Scenario
   - 10 million requests/month
   - Avg 200ms execution time
   - 512 MB memory per request
   - Traffic pattern: Variable (1K-50K req/hr)

   ## Option 1: AWS Lambda
   **Monthly Cost**: $124
   - Requests: 10M × $0.20/1M = $2
   - Compute: 10M × 0.2s × 0.5GB × $0.0000166667 = $122
   - **Pros**: Auto-scaling, pay-per-use, no idle costs
   - **Cons**: Cold starts, 15min timeout

   ## Option 2: ECS Fargate
   **Monthly Cost**: $219
   - vCPU: 0.5 × 730hrs × $0.04048 = $14.78
   - Memory: 1GB × 730hrs × $0.004445 = $3.24
   - Load Balancer: $16.20
   - Need ~10 tasks for peak: $180 (avg load)
   - **Pros**: Consistent performance, long-running jobs OK
   - **Cons**: Over-provisioning for low traffic periods

   ## Recommendation
   **Use Lambda** - Save $95/month (43%)

   **Reasoning**:
   - Variable traffic benefits from pay-per-use
   - Short execution time ideal for Lambda
   - Cost grows linearly with usage
   - Can optimize with provisioned concurrency if needed
   ```

### Outcome
- Clear cost comparison: Lambda saves 43%
- Decision justified with data
- Scalability implications understood

---

## Example 4: Quarterly Cost Review

### Scenario
Preparing quarterly business review, need comprehensive financial report.

### Invocation
```
/cfo quarterly financial report
```

### What Happens

1. **Comprehensive Analysis**
   - Scans entire codebase
   - Analyzes recent trends (if billing data available)
   - Benchmarks against industry standards

2. **Executive Report**
   ```markdown
   # Q3 2024 Cloud Financial Report

   ## Executive Summary
   **Total Cloud Spend**: $15,234/month (avg)
   **QoQ Change**: +12% (Q2: $13,602)
   **Run Rate**: $182,808/year
   **Top 3 Drivers**: Compute (55%), Database (23%), Storage (12%)

   ### Status
   - 🟢 Budget: Within 5% of forecast
   - 🟡 Growth: Slightly ahead of revenue growth (+9%)
   - 🟢 Optimization: Saved $2,400 this quarter

   ## By Environment
   - Production: $12,187 (80%)
   - Staging: $2,134 (14%)
   - Development: $913 (6%)

   ## Key Achievements
   1. Migrated to reserved instances (saved $1,800/month)
   2. Implemented auto-scaling (reduced dev costs 40%)
   3. Cleaned up orphaned resources (saved $600/month)

   ## Recommendations for Q4
   1. **Commit to Savings Plans** (save $3,000/month)
   2. **Implement tiered storage** (save $800/month)
   3. **Optimize database queries** (reduce RDS size, save $1,200/month)

   **Total Q4 Savings Potential**: $5,000/month ($60K annual)
   ```

### Outcome
- Clear quarterly trends
- Concrete savings achievements
- Roadmap for next quarter

---

## Example 5: Revenue Strategy Planning

### Scenario
Need to monetize API to offset infrastructure costs.

### Invocation
```
/cfo revenue strategy for API product, current costs $8,500/month
```

### What Happens

1. **Revenue Analysis**
   - Reviews current cost structure
   - Analyzes API usage patterns (from code)
   - References revenue model best practices

2. **Strategy Report**
   ```markdown
   # Revenue Strategy - API Monetization

   ## Current Situation
   **Monthly Costs**: $8,500
   **Current Revenue**: $0 (free API)
   **Gap to Cover**: $8,500/month

   ## Recommended Pricing Model

   ### Freemium + Usage-Based

   **Free Tier**:
   - 10,000 requests/month
   - Community support
   - Public projects only
   - **Target**: Developers, testing

   **Starter** ($29/month):
   - 500,000 requests/month ($0.058 per 1K)
   - Email support
   - Private projects
   - **Target**: Small projects, side hustles

   **Professional** ($99/month):
   - 5,000,000 requests/month ($0.020 per 1K)
   - Priority support
   - SLA guarantee
   - Advanced analytics
   - **Target**: Growing startups

   **Enterprise** (Custom):
   - Unlimited requests (volume pricing)
   - Dedicated support
   - Custom SLA
   - On-premise options
   - **Target**: Large companies

   ## Revenue Projections

   **Conservative** (100 customers, 70% free, 25% Starter, 5% Pro):
   - Free: 70 × $0 = $0
   - Starter: 25 × $29 = $725/month
   - Pro: 5 × $99 = $495/month
   - **Total**: $1,220/month (14% cost coverage)

   **Growth** (500 customers, 60% free, 30% Starter, 8% Pro, 2% Enterprise):
   - Free: 300 × $0 = $0
   - Starter: 150 × $29 = $4,350/month
   - Pro: 40 × $99 = $3,960/month
   - Enterprise: 10 × $500 = $5,000/month
   - **Total**: $13,310/month (157% cost coverage) ✓

   **Mature** (2000 customers, 50% free, 35% Starter, 12% Pro, 3% Enterprise):
   - Total: $42,940/month (505% cost coverage)

   ## Path to Profitability
   - **Month 1-3**: Launch pricing, convert 5% of free users
   - **Month 4-6**: Optimize pricing based on data, reach 50 paid customers
   - **Month 7-12**: Scale to 200 paid customers, break even
   - **Year 2**: Achieve 500+ paid customers, 2x cost coverage

   ## Implementation Steps
   1. Set up usage tracking/metering
   2. Implement billing system (Stripe)
   3. Create pricing page
   4. Enable API key management
   5. Launch with 14-day free trial
   ```

### Outcome
- Clear monetization path
- Realistic revenue projections
- Break-even timeline: 7-12 months

---

## Example 6: Cost Optimization Sprint

### Scenario
CEO wants to cut cloud costs by 30% this quarter.

### Invocation
```
/cfo find 30% cost reduction opportunities
```

### What Happens

1. **Deep Analysis**
   - Scans for all optimization opportunities
   - Prioritizes by impact, effort, risk
   - Creates actionable roadmap

2. **Optimization Plan**
   ```markdown
   # Cost Optimization Plan - Target: 30% Reduction

   **Current Monthly Spend**: $24,500
   **Target**: $17,150 (save $7,350/month)

   ## Tier 1: Quick Wins (Week 1) - $1,845/month (7.5%)

   ### Delete Unused Resources
   - **Impact**: $720/month
   - **Effort**: 2 hours
   - **Risk**: Low
   - **Details**:
     - 15 orphaned EBS volumes: $450/month
     - 8 unattached Elastic IPs: $72/month
     - 47 old snapshots: $198/month

   ### Rightsize Over-Provisioned Instances
   - **Impact**: $925/month
   - **Effort**: 1 day
   - **Risk**: Low (test in staging first)
   - **Details**:
     - db.m5.2xlarge → db.m5.xlarge (avg CPU 18%): $420/month
     - 4× c5.xlarge → c5.large (avg CPU 22%): $505/month

   ### Enable Auto-Shutdown (Dev/Test)
   - **Impact**: $200/month
   - **Effort**: 4 hours
   - **Risk**: None
   - **Details**: Shutdown dev instances nights & weekends (save 70% of time)

   ## Tier 2: Strategic (Weeks 2-4) - $3,675/month (15%)

   ### Purchase Reserved Instances
   - **Impact**: $2,100/month
   - **Effort**: 1 week (analysis + purchase)
   - **Risk**: Low (only for steady workloads)
   - **Details**: 8 instances running 24/7, 1-year standard RI, 42% savings

   ### Implement S3 Lifecycle Policies
   - **Impact**: $475/month
   - **Effort**: 3 days
   - **Risk**: Low
   - **Details**:
     - Move >90 day data to IA: $325/month
     - Archive >365 day logs to Glacier: $150/month

   ### Optimize Data Transfer
   - **Impact**: $800/month
   - **Effort**: 1 week
   - **Risk**: Low
   - **Details**:
     - Implement CloudFront CDN: $650/month (vs direct S3 egress)
     - Keep data in same region: $150/month

   ### Database Query Optimization
   - **Impact**: $300/month
   - **Effort**: 2 weeks
   - **Risk**: Medium (requires testing)
   - **Details**: Add indexes, optimize queries, reduce RDS instance size

   ## Tier 3: Architectural (Months 2-3) - $2,850/month (11.6%)

   ### Migrate to Spot Instances
   - **Impact**: $1,500/month
   - **Effort**: 3 weeks
   - **Risk**: Medium (requires fault-tolerance)
   - **Details**: Batch jobs, ML training, dev environments

   ### Serverless Migration
   - **Impact**: $900/month
   - **Effort**: 6 weeks
   - **Risk**: Medium
   - **Details**: Migrate low-traffic APIs to Lambda

   ### Database Consolidation
   - **Impact**: $450/month
   - **Effort**: 4 weeks
   - **Risk**: High
   - **Details**: Merge 3 small databases into one larger (economies of scale)

   ## Total Savings: $8,370/month (34.2%) ✓ EXCEEDS TARGET

   ## Recommended Roadmap
   **Week 1**: Quick Wins → $1,845 saved
   **Week 2-4**: Strategic → cumulative $5,520 saved
   **Month 2-3**: Architectural → cumulative $8,370 saved

   **Risk-Adjusted Target** (excluding high-risk items):
   $7,920/month (32.3% reduction) - Still exceeds 30% goal ✓
   ```

### Outcome
- Exceeds 30% target (34.2% possible)
- Phased approach manages risk
- Quick wins provide immediate value

---

## Example 7: Pricing Strategy Validation

### Scenario
Considering raising prices, need financial impact analysis.

### Invocation
```
/cfo analyze impact of raising Pro plan from $99 to $129
```

### What Happens

1. **Impact Modeling**
   - Estimates churn based on industry benchmarks
   - Calculates revenue impact
   - Analyzes customer segments

2. **Analysis Report**
   ```markdown
   # Pricing Change Impact Analysis

   ## Proposed Change
   **Current**: Pro plan at $99/month
   **Proposed**: Pro plan at $129/month (+30%)

   ## Current State
   - 147 Pro customers
   - $14,553/month revenue
   - Average customer tenure: 14 months

   ## Impact Scenarios

   ### Optimistic (5% churn)
   - Lost customers: 7
   - Remaining: 140
   - New revenue: 140 × $129 = $18,060/month
   - **Net Impact**: +$3,507/month (+24%) ✓

   ### Realistic (10% churn)
   - Lost customers: 15
   - Remaining: 132
   - New revenue: 132 × $129 = $17,028/month
   - **Net Impact**: +$2,475/month (+17%) ✓

   ### Pessimistic (20% churn)
   - Lost customers: 29
   - Remaining: 118
   - New revenue: 118 × $129 = $15,222/month
   - **Net Impact**: +$669/month (+5%) ⚠️

   ## LTV Impact
   **Current LTV**: $99 × 14 months = $1,386
   **New LTV** (10% churn): $129 × 12.6 months = $1,625 (+17%)

   ## Recommendations

   ### ✅ Proceed with Price Increase IF:
   1. Grandfather existing customers (reduces churn risk)
   2. Add new features to justify increase
   3. Communicate value clearly
   4. Offer annual discount (15-20%)

   ### Implementation Strategy
   1. **Month 1**: Announce price change (60-day notice)
   2. **Month 2**: Grandfather existing, apply to new only
   3. **Month 3**: Monitor churn rate
   4. **Month 4**: If churn <10%, apply to renewals

   ### Expected Outcome
   - Realistic scenario: +$2,475/month revenue
   - Covers 2 additional engineers' infrastructure costs
   - Improves margin from 68% to 73%
   ```

### Outcome
- Data-driven pricing decision
- Risk mitigation strategy (grandfathering)
- Clear rollout plan

---

## Example 8: Multi-Cloud Cost Comparison

### Scenario
Considering AWS vs GCP for new region deployment.

### Invocation
```
/cfo compare AWS us-east-1 vs GCP us-central1 for our workload
```

### What Happens

1. **Workload Analysis**
   - Identifies current AWS resource usage
   - Maps to equivalent GCP services
   - Calculates pricing for both

2. **Comparison Report**
   ```markdown
   # Multi-Cloud Cost Comparison

   ## Workload Profile
   - 10× VM instances (4 vCPU, 16 GB RAM)
   - 2 TB storage
   - 500 GB/month data egress
   - PostgreSQL database (8 vCPU, 32 GB RAM)
   - 100GB Redis cache

   ## AWS (us-east-1)
   | Service | Type | Quantity | Monthly Cost |
   |---------|------|----------|--------------|
   | EC2 | m5.xlarge | 10 | $1,401 |
   | EBS | gp3 | 2 TB | $160 |
   | Data Transfer | Egress | 500 GB | $45 |
   | RDS PostgreSQL | db.r5.xlarge | 1 | $350 |
   | ElastiCache | cache.r5.large | 1 | $146 |
   | **Total** | | | **$2,102** |

   ## GCP (us-central1)
   | Service | Type | Quantity | Monthly Cost |
   |---------|------|----------|--------------|
   | Compute Engine | n2-standard-4 | 10 | $1,220 |
   | Persistent Disk | SSD | 2 TB | $340 |
   | Data Transfer | Egress | 500 GB | $60 |
   | Cloud SQL | db-custom-8-32 | 1 | $384 |
   | Memorystore | Redis M2 | 1 | $127 |
   | **Total** | | | **$2,131** |

   ## Cost Comparison
   - **AWS**: $2,102/month
   - **GCP**: $2,131/month
   - **Difference**: +$29/month (+1.4% on GCP)

   ## With Committed Use Discounts
   **AWS (1-year RI)**:
   - Total: $1,459/month (save $643, 31%)

   **GCP (1-year CUD)**:
   - Total: $1,496/month (save $635, 30%)

   ## Other Considerations

   ### AWS Pros
   - More mature services
   - Better third-party integrations
   - Your team has AWS expertise
   - Current monitoring/tooling in place

   ### GCP Pros
   - Superior BigQuery (if adding analytics)
   - Better Kubernetes (GKE)
   - Cleaner pricing model
   - Free egress to some Google services

   ## Recommendation
   **Stay with AWS** for this deployment

   **Reasoning**:
   - Nearly identical cost (~1% difference)
   - Avoid multi-cloud complexity
   - Leverage existing AWS expertise
   - Reuse infrastructure-as-code
   - Unified billing and monitoring

   **Exception**: Consider GCP if planning heavy analytics workload (BigQuery advantage)
   ```

### Outcome
- Quantified cost difference (minimal)
- Decision factors beyond just cost
- Avoided unnecessary complexity

---

## Tips for Effective CFO Usage

### 1. Be Specific
**Instead of**: `/cfo help with costs`
**Try**: `/cfo find Lambda cold start impact on costs`

### 2. Provide Context
**Instead of**: `/cfo reduce costs`
**Try**: `/cfo reduce costs by 20%, preserving production reliability`

### 3. Include Billing Data
**Instead of**: Relying on estimates
**Try**: `/cfo analyze billing data at ./aws-june.csv` (actual data)

### 4. Regular Reviews
- **Weekly**: Quick cost check
- **Monthly**: Detailed analysis
- **Quarterly**: Strategic planning
- **Before major changes**: Cost impact assessment

### 5. Combine with Other Tools
```
# In CI/CD pipeline
python .claude/skills/cfo/scripts/analyze_costs.py --project-root . --output cost-report.md

# Review in PR
/cfo analyze cost impact of changes in this PR
```

---

## Next Steps

Ready to use the CFO skill? Try:

1. **Start Simple**: `/cfo` for comprehensive analysis
2. **Review Output**: Understand your cost baseline
3. **Act on Quick Wins**: Implement low-effort savings
4. **Plan Strategic Changes**: Roadmap bigger optimizations
5. **Monitor Progress**: Regular reviews to track savings

**Need help?** See `.claude/skills/cfo/skill.md` for detailed documentation.
