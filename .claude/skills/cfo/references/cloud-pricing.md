# Cloud Pricing Reference

> Quick reference for common cloud service pricing across major providers.

**Last Updated**: 2025-01-15
**Note**: Prices are approximate and vary by region. Always check official pricing pages for current rates.

---

## AWS (Amazon Web Services)

### Compute

| Service | Type | Price (US East) | Unit |
|---------|------|-----------------|------|
| EC2 - t3.micro | General Purpose | $0.0104/hr (~$7.50/mo) | On-Demand |
| EC2 - t3.small | General Purpose | $0.0208/hr (~$15/mo) | On-Demand |
| EC2 - t3.medium | General Purpose | $0.0416/hr (~$30/mo) | On-Demand |
| EC2 - m5.large | General Purpose | $0.096/hr (~$70/mo) | On-Demand |
| Lambda | Serverless | $0.20 per 1M requests + $0.00001667/GB-sec | Usage |
| Fargate | Containers | $0.04048/vCPU-hr + $0.004445/GB-hr | Usage |

**Savings Options**:
- Reserved Instances: Up to 72% savings (1-3 year commitment)
- Spot Instances: Up to 90% savings (interruptible)
- Savings Plans: Up to 72% savings (flexible commitment)

### Storage

| Service | Type | Price | Unit |
|---------|------|-------|------|
| S3 Standard | Object Storage | $0.023/GB | Per month |
| S3 Infrequent Access | Object Storage | $0.0125/GB | Per month |
| S3 Glacier | Archive | $0.004/GB | Per month |
| EBS gp3 | Block Storage | $0.08/GB | Per month |
| EFS | File Storage | $0.30/GB | Per month |

**Data Transfer**:
- First 100 GB/month: Free
- Next 10 TB/month: $0.09/GB
- Next 40 TB/month: $0.085/GB

### Database

| Service | Type | Price (US East) | Unit |
|---------|------|-----------------|------|
| RDS - db.t3.micro | MySQL/PostgreSQL | $0.017/hr (~$12/mo) | On-Demand |
| RDS - db.t3.small | MySQL/PostgreSQL | $0.034/hr (~$25/mo) | On-Demand |
| DynamoDB | NoSQL | $0.25/GB storage + $1.25 per million writes | On-Demand |
| DynamoDB | NoSQL | $0.00013/WRU + $0.00013/10RRU | Provisioned |
| Aurora Serverless v2 | MySQL/PostgreSQL | $0.12 per ACU-hour | Usage |
| ElastiCache - cache.t3.micro | Redis/Memcached | $0.017/hr (~$12/mo) | On-Demand |

### Networking

| Service | Description | Price | Unit |
|---------|-------------|-------|------|
| CloudFront | CDN | $0.085/GB | Data transfer |
| API Gateway | REST API | $3.50 per million requests | Usage |
| API Gateway | HTTP API | $1.00 per million requests | Usage |
| Application Load Balancer | Load Balancing | $0.0225/hr + $0.008/LCU-hr | Usage |
| Route 53 | DNS | $0.50/hosted zone + $0.40/million queries | Monthly |

**Official Pricing**: https://aws.amazon.com/pricing/

---

## GCP (Google Cloud Platform)

### Compute

| Service | Type | Price (US regions) | Unit |
|---------|------|-------------------|------|
| Compute Engine - e2-micro | General Purpose | $0.0084/hr (~$6/mo) | On-Demand |
| Compute Engine - e2-small | General Purpose | $0.0168/hr (~$12/mo) | On-Demand |
| Compute Engine - e2-medium | General Purpose | $0.0335/hr (~$24/mo) | On-Demand |
| Cloud Functions | Serverless | $0.40 per million invocations + $0.0000025/GB-sec | Usage |
| Cloud Run | Containers | $0.00002400/vCPU-sec + $0.00000250/GiB-sec | Usage |

**Savings Options**:
- Committed Use Discounts: Up to 57% savings (1-3 year)
- Spot VMs: Up to 91% savings (preemptible)
- Sustained Use Discounts: Automatic up to 30% for consistent use

### Storage

| Service | Type | Price | Unit |
|---------|------|-------|------|
| Cloud Storage Standard | Object Storage | $0.020/GB | Per month |
| Cloud Storage Nearline | Infrequent Access | $0.010/GB | Per month |
| Cloud Storage Coldline | Archive | $0.004/GB | Per month |
| Persistent Disk SSD | Block Storage | $0.170/GB | Per month |
| Filestore Basic | File Storage | $0.20/GB | Per month |

**Data Transfer**:
- Within same region: Free
- To worldwide (0-1 TB): $0.12/GB
- To worldwide (1-10 TB): $0.11/GB

### Database

| Service | Type | Price (US regions) | Unit |
|---------|------|-------------------|------|
| Cloud SQL - db-f1-micro | MySQL/PostgreSQL | $0.0150/hr (~$11/mo) | On-Demand |
| Cloud SQL - db-g1-small | MySQL/PostgreSQL | $0.0500/hr (~$36/mo) | On-Demand |
| Firestore | NoSQL | $0.18/GB storage + $0.06 per 100K reads | Usage |
| BigQuery | Data Warehouse | $0.02/GB storage + $6.25/TB queries | Usage |
| Cloud Spanner | Distributed SQL | $0.90/node-hr (~$650/node/mo) | Usage |

### Networking

| Service | Description | Price | Unit |
|---------|-------------|-------|------|
| Cloud CDN | CDN | $0.08/GB | Data transfer |
| API Gateway | API Management | $3.00 per million calls | Usage |
| Cloud Load Balancing | Load Balancing | $0.025/hr + $0.008/forwarding rule hour | Usage |
| Cloud DNS | DNS | $0.20/million queries | Monthly |

**Official Pricing**: https://cloud.google.com/pricing

---

## Azure (Microsoft Azure)

### Compute

| Service | Type | Price (East US) | Unit |
|---------|------|-----------------|------|
| Virtual Machines - B1S | Burstable | $0.0104/hr (~$7.50/mo) | Pay-as-you-go |
| Virtual Machines - B2S | Burstable | $0.0416/hr (~$30/mo) | Pay-as-you-go |
| Azure Functions | Serverless | $0.20 per million executions + $0.000016/GB-sec | Consumption |
| Container Instances | Containers | $0.0000125/vCPU-sec + $0.0000014/GB-sec | Usage |

**Savings Options**:
- Reserved Instances: Up to 72% savings (1-3 year)
- Spot VMs: Up to 90% savings (evictable)
- Azure Hybrid Benefit: Use existing licenses

### Storage

| Service | Type | Price | Unit |
|---------|------|-------|------|
| Blob Storage Hot | Object Storage | $0.0184/GB | Per month |
| Blob Storage Cool | Infrequent Access | $0.0100/GB | Per month |
| Blob Storage Archive | Archive | $0.00099/GB | Per month |
| Managed Disks SSD | Block Storage | $0.12/GB | Per month |
| Azure Files | File Storage | $0.06/GB | Per month |

**Data Transfer**:
- First 100 GB/month: Free
- 100 GB - 10 TB: $0.087/GB
- 10 TB - 50 TB: $0.083/GB

### Database

| Service | Type | Price (East US) | Unit |
|---------|------|-----------------|------|
| SQL Database - Basic | Relational | $4.90/month | Per database |
| SQL Database - S0 | Relational | $15/month | Per database |
| Cosmos DB | NoSQL | $0.25/GB + $0.008/10K RUs | Provisioned |
| Database for PostgreSQL | Managed PostgreSQL | $0.018/hr (~$13/mo) | Burstable B1ms |
| Redis Cache - Basic C0 | Cache | $0.016/hr (~$12/mo) | Basic tier |

### Networking

| Service | Description | Price | Unit |
|---------|-------------|-------|------|
| Azure CDN | CDN | $0.081/GB | Data transfer |
| API Management | API Gateway | $0.063/hr (~$46/mo) | Developer tier |
| Application Gateway | Load Balancing | $0.125/hr + $0.008/capacity unit | Usage |
| Traffic Manager | DNS Load Balancing | $0.54/million queries | Monthly |

**Official Pricing**: https://azure.microsoft.com/en-us/pricing/

---

## Other Common Services

### Vercel
- **Hobby**: $0 (personal projects, limited)
- **Pro**: $20/month per user
- **Enterprise**: Custom pricing
- **Serverless Functions**: Included (100 GB-hours on Pro)
- **Bandwidth**: 100 GB/month on Pro, then $40/100GB

### Netlify
- **Starter**: $0 (limited)
- **Pro**: $19/month
- **Business**: $99/month
- **Bandwidth**: 100 GB/month on Pro, then $55/100GB
- **Build Minutes**: 300 min/month on Pro, then $7/500 min

### Heroku
- **Eco Dyno**: $5/month (shared)
- **Basic Dyno**: $7/month (dedicated)
- **Standard 1X**: $25/month
- **Standard 2X**: $50/month
- **Postgres Mini**: $5/month (10K rows)
- **Postgres Basic**: $9/month (10M rows)

### MongoDB Atlas
- **M0 (Free)**: $0 (512 MB storage)
- **M10 (Shared)**: $57/month
- **M20 (Dedicated)**: $121/month
- **M30**: $225/month
- **Serverless**: $0.30/million reads, $1.00/million writes

### Cloudflare
- **Free**: $0 (unlimited bandwidth, basic DDoS)
- **Pro**: $20/month
- **Business**: $200/month
- **Workers**: $5/10M requests

---

## Pricing Trends & Patterns

### General Observations

1. **Compute follows similar pricing**: AWS, GCP, and Azure have converged on similar pricing for comparable instance types
2. **Discounts matter**: Reserved capacity can save 50-70% for predictable workloads
3. **Egress is expensive**: Data transfer out is often a hidden cost (2-10x more than storage)
4. **Free tiers exist**: Most providers offer free tiers for learning/testing
5. **Enterprise discounts**: Large customers can negotiate 20-40% off list prices

### Cost Optimization Priorities

**By Impact**:
1. Compute (typically 50-60% of bill)
2. Data transfer (typically 15-25% of bill)
3. Storage (typically 10-20% of bill)
4. Everything else (typically 5-15%)

**Quick Wins**:
- Delete unused resources (orphaned volumes, snapshots)
- Rightsize over-provisioned instances
- Use cheaper storage tiers for infrequent data
- Enable auto-shutdown for dev/test

---

## Regional Price Variations

Prices vary by region. General patterns:

| Region Type | Price Multiplier | Examples |
|-------------|------------------|----------|
| US East/West | 1.0x (baseline) | us-east-1, us-west-2 |
| Europe | 1.1-1.2x | eu-west-1, eu-central-1 |
| Asia Pacific | 1.15-1.25x | ap-southeast-1, ap-northeast-1 |
| South America | 1.3-1.5x | sa-east-1 |

**Tip**: Choose regions close to users, but consider cost differences for dev/test environments.

---

## API/SaaS Service Pricing Models

Common patterns for third-party APIs:

| Model | Description | Example |
|-------|-------------|---------|
| Per-Request | Pay per API call | $0.001 per request |
| Per-User | Monthly fee per user | $10/user/month |
| Tiered | Price breaks at volumes | 0-10K: $0.01, 10K-100K: $0.008 |
| Freemium | Free tier + paid | 1K requests free, then $0.001 |
| Flat Rate | Unlimited for fixed price | $99/month unlimited |

---

## Quick Cost Estimation Formulas

### Compute
```
Monthly = (hourly_rate × 730 hours) × (1 - discount_rate)
```

### Storage
```
Monthly = GB_stored × price_per_GB × retention_months
```

### Data Transfer
```
Monthly = GB_transferred_out × egress_price_per_GB
```

### Database
```
Monthly = (compute_cost + storage_cost + IO_cost) × (1 - discount_rate)
```

---

## References

- **AWS Pricing Calculator**: https://calculator.aws/
- **GCP Pricing Calculator**: https://cloud.google.com/products/calculator
- **Azure Pricing Calculator**: https://azure.microsoft.com/en-us/pricing/calculator/
- **Cloud Cost Comparison**: https://www.cloudcomparison.io/
- **Instances.vantage.sh**: https://instances.vantage.sh/ (compare instance types)

---

**Disclaimer**: Prices change frequently. Always verify current pricing before making decisions.
