# Cost Categories & Taxonomy

> Standard classification system for cloud costs to enable consistent analysis and reporting.

---

## Primary Cost Categories

### 1. Compute

**Definition**: Resources that provide processing power.

**Subcategories**:
- **Virtual Machines**: EC2, Compute Engine, Azure VMs
- **Serverless Functions**: Lambda, Cloud Functions, Azure Functions
- **Containers**: ECS, GKE, AKS, Fargate, Cloud Run
- **Bare Metal**: Dedicated hosts
- **Batch Processing**: Batch, Cloud Tasks
- **HPC**: High-performance computing instances

**Cost Drivers**:
- Instance type/size
- Operating system
- Usage hours
- Licensing (Windows, RHEL)
- Reserved vs on-demand vs spot

**Typical % of Total**: 40-60%

### 2. Storage

**Definition**: Data persistence and retrieval services.

**Subcategories**:
- **Object Storage**: S3, Cloud Storage, Blob Storage
- **Block Storage**: EBS, Persistent Disks, Managed Disks
- **File Storage**: EFS, Filestore, Azure Files
- **Archive**: Glacier, Coldline, Archive Blob
- **Backups**: Backup solutions, snapshots
- **CDN**: CloudFront, Cloud CDN, Azure CDN

**Cost Drivers**:
- Storage capacity (GB/TB)
- Storage class (hot/cool/archive)
- Data transfer out
- Request count (PUT/GET)
- Retrieval fees

**Typical % of Total**: 10-25%

### 3. Database

**Definition**: Managed database services.

**Subcategories**:
- **Relational**: RDS, Cloud SQL, Azure SQL
- **NoSQL**: DynamoDB, Firestore, Cosmos DB
- **In-Memory**: ElastiCache, Memorystore, Redis Cache
- **Data Warehouse**: Redshift, BigQuery, Synapse
- **Graph**: Neptune, CosmosDB Gremlin
- **Time Series**: Timestream, Bigtable

**Cost Drivers**:
- Instance size
- Storage capacity
- IOPS/throughput
- Backup retention
- Multi-AZ/replication
- Reserved vs on-demand

**Typical % of Total**: 15-30%

### 4. Networking

**Definition**: Data transfer and connectivity services.

**Subcategories**:
- **Data Transfer Out**: Egress from cloud
- **Data Transfer Between Regions**: Cross-region
- **Load Balancing**: ALB, Cloud Load Balancing, Azure LB
- **DNS**: Route 53, Cloud DNS, Azure DNS
- **VPN**: VPN Gateway, Cloud VPN
- **Direct Connect**: Direct Connect, Interconnect, ExpressRoute
- **API Gateway**: API Gateway, Cloud Endpoints

**Cost Drivers**:
- Data transfer volume (GB/TB)
- Number of requests
- Load balancer hours
- Bandwidth provisioned

**Typical % of Total**: 10-20%

### 5. Security & Identity

**Definition**: Security, compliance, and access management.

**Subcategories**:
- **Secrets Management**: Secrets Manager, Secret Manager, Key Vault
- **Key Management**: KMS, Cloud KMS, Key Vault
- **Web Application Firewall**: WAF, Cloud Armor, Azure WAF
- **DDoS Protection**: Shield, Cloud Armor, DDoS Protection
- **Identity**: IAM, Cloud Identity, Azure AD
- **Certificate Management**: ACM, Certificate Manager

**Cost Drivers**:
- Number of secrets/keys
- Requests per month
- WAF rules evaluated
- DDoS protection tier

**Typical % of Total**: 1-5%

### 6. Observability

**Definition**: Monitoring, logging, and tracing services.

**Subcategories**:
- **Monitoring**: CloudWatch, Cloud Monitoring, Azure Monitor
- **Logging**: CloudWatch Logs, Cloud Logging, Log Analytics
- **Tracing**: X-Ray, Cloud Trace, Application Insights
- **Alerting**: SNS, Cloud Pub/Sub, Azure Alerts
- **Dashboards**: Managed Grafana, Looker, Azure Dashboards

**Cost Drivers**:
- Metrics ingested
- Logs ingested and stored
- Retention period
- Number of traces
- API requests

**Typical % of Total**: 5-15%

### 7. Developer Tools

**Definition**: Tools for development, CI/CD, and deployment.

**Subcategories**:
- **Source Control**: CodeCommit, Cloud Source Repositories
- **CI/CD**: CodePipeline, Cloud Build, Azure DevOps
- **Container Registry**: ECR, Artifact Registry, Container Registry
- **Deployment**: CodeDeploy, Cloud Deploy
- **Testing**: Device Farm, Test Lab

**Cost Drivers**:
- Build minutes
- Storage for artifacts
- Number of pipelines
- Active users

**Typical % of Total**: 1-5%

### 8. AI/ML

**Definition**: Machine learning and artificial intelligence services.

**Subcategories**:
- **Model Training**: SageMaker, AI Platform, Azure ML
- **Inference**: SageMaker Inference, Vertex AI, Azure ML
- **Pre-trained APIs**: Rekognition, Vision API, Cognitive Services
- **Data Labeling**: Ground Truth, Data Labeling
- **ML Infrastructure**: Specialized instances (P3, GPU VMs)

**Cost Drivers**:
- Training hours
- Instance types (GPU/TPU)
- Inference requests
- Data processed
- API calls

**Typical % of Total**: 0-30% (highly variable)

### 9. Integration & Messaging

**Definition**: Services for async communication and integration.

**Subcategories**:
- **Message Queues**: SQS, Cloud Pub/Sub, Service Bus
- **Event Streams**: Kinesis, Pub/Sub, Event Hubs
- **Workflow**: Step Functions, Cloud Workflows, Logic Apps
- **API Management**: API Gateway, Apigee, API Management
- **Event Bus**: EventBridge, Eventarc, Event Grid

**Cost Drivers**:
- Message volume
- Data processed
- Workflow executions
- API calls

**Typical % of Total**: 2-8%

### 10. Analytics & Big Data

**Definition**: Data processing and analytics platforms.

**Subcategories**:
- **Data Lake**: S3 + Athena, BigQuery, Synapse
- **ETL**: Glue, Dataflow, Data Factory
- **Streaming**: Kinesis, Dataflow, Stream Analytics
- **Business Intelligence**: QuickSight, Looker, Power BI
- **Search**: OpenSearch, Elastic, Azure Search

**Cost Drivers**:
- Data processed
- Queries run
- Storage
- Cluster hours
- Streaming volume

**Typical % of Total**: 5-20%

### 11. Support & Other

**Definition**: Support plans and miscellaneous services.

**Subcategories**:
- **Support Plans**: Business, Enterprise support
- **Training & Certification**: Cloud training
- **Professional Services**: Consulting, implementation
- **Marketplace**: Third-party services
- **Credits**: Promotional credits (negative cost)

**Cost Drivers**:
- Support tier
- Number of users
- Contract terms

**Typical % of Total**: 5-15%

---

## Secondary Classification Dimensions

### By Environment

- **Production**: Customer-facing workloads
- **Staging**: Pre-production testing
- **Development**: Active development
- **Testing**: QA and integration tests
- **Sandbox**: Experimentation

**Purpose**: Identify non-production waste, implement auto-shutdown policies.

### By Team/Department

- **Engineering**: Development teams
- **Data**: Data science/analytics
- **Infrastructure**: Platform/DevOps
- **Security**: Security team
- **Sales/Marketing**: Customer-facing apps

**Purpose**: Showback/chargeback, accountability.

### By Product/Project

- **Product A**: Mobile app
- **Product B**: Web platform
- **Product C**: API service
- **Shared Infrastructure**: Common services

**Purpose**: Unit economics, product profitability.

### By Cost Type

- **Usage-Based**: Pay for what you use
- **Reserved Capacity**: Committed spend
- **Spot/Preemptible**: Discounted interruptible
- **Flat Rate**: Fixed monthly fees

**Purpose**: Identify optimization opportunities (commitment vs flexibility).

### By Lifecycle

- **Active**: Currently used
- **Idle**: Provisioned but unused
- **Scheduled**: Auto-start/stop
- **Terminated**: Stopped/deleted

**Purpose**: Waste identification, cost attribution.

---

## Cost Allocation Hierarchy

```
Total Cloud Spend
├── By Provider
│   ├── AWS
│   ├── GCP
│   └── Azure
├── By Category (Primary)
│   ├── Compute
│   ├── Storage
│   ├── Database
│   └── ...
├── By Environment
│   ├── Production
│   ├── Staging
│   └── Development
├── By Team
│   ├── Team A
│   ├── Team B
│   └── Shared
└── By Product
    ├── Product 1
    ├── Product 2
    └── Platform
```

**Use Case**: Drill-down analysis from top-level trends to specific resources.

---

## Standard Tags for Cost Allocation

### Required Tags

```yaml
Environment:
  values: [production, staging, development, test, sandbox]

Owner:
  format: email or team name
  example: "platform-team" or "eng@company.com"

Project:
  format: project code or name
  example: "mobile-app" or "PRJ-123"

CostCenter:
  format: finance department code
  example: "CC-ENG-001"
```

### Recommended Tags

```yaml
Application:
  example: "api-gateway"

Department:
  values: [engineering, data, security, operations]

Customer:
  example: "customer-xyz" (for multi-tenant)

DataClassification:
  values: [public, internal, confidential, restricted]

AutoShutdown:
  values: [true, false]
  schedule: "weekdays-only" or "never"

Compliance:
  values: [pci, hipaa, sox, none]
```

---

## Cost Attribution Models

### Direct Attribution

**Method**: Resource has explicit tag linking to cost center.

**Example**: EC2 instance tagged with `Project: mobile-app` → 100% allocated to mobile app.

**Pros**: Clear ownership, accurate
**Cons**: Doesn't handle shared resources

### Proportional Attribution

**Method**: Shared resources split based on usage metrics.

**Example**: Shared data pipeline costs split by data volume per team.

**Metrics for Proportion**:
- Compute: CPU hours or memory-GB hours
- Storage: GB stored
- Network: Bandwidth used
- Database: Query count or IOPS

**Pros**: Fair for shared services
**Cons**: Requires metric collection, more complex

### Fixed Percentage

**Method**: Shared costs split by fixed percentages.

**Example**: Platform team costs: 50% to Product A, 30% to Product B, 20% to Product C.

**Pros**: Simple, predictable
**Cons**: May not reflect actual usage

---

## Cost Analysis Queries

### By Category

```sql
SELECT
  category,
  SUM(cost) as total_cost,
  SUM(cost) / (SELECT SUM(cost) FROM costs) * 100 as percentage
FROM costs
GROUP BY category
ORDER BY total_cost DESC;
```

### By Environment

```sql
SELECT
  environment,
  category,
  SUM(cost) as total_cost
FROM costs
GROUP BY environment, category
ORDER BY environment, total_cost DESC;
```

### Waste Analysis

```sql
SELECT
  resource_id,
  cost,
  utilization,
  CASE
    WHEN utilization < 0.1 THEN 'Zombie (delete)'
    WHEN utilization < 0.3 THEN 'Underutilized (rightsize)'
    ELSE 'Normal'
  END as recommendation
FROM costs
WHERE utilization < 0.5
ORDER BY cost DESC;
```

---

## Common Cost Patterns by Industry

### SaaS Applications

**Typical Breakdown**:
- Compute: 50%
- Database: 25%
- Storage: 10%
- Networking: 10%
- Other: 5%

**Key Metric**: Cost per active user

### E-Commerce

**Typical Breakdown**:
- Compute: 40%
- Database: 30%
- CDN/Networking: 20%
- Storage: 5%
- Other: 5%

**Key Metric**: Cost per transaction

### Data/Analytics

**Typical Breakdown**:
- Compute: 35%
- Storage: 30%
- Database/Analytics: 25%
- Networking: 5%
- Other: 5%

**Key Metric**: Cost per GB processed

### Media/Gaming

**Typical Breakdown**:
- CDN/Networking: 40%
- Compute: 30%
- Storage: 20%
- Database: 5%
- Other: 5%

**Key Metric**: Cost per user or cost per stream

---

## Quick Reference

### High-Impact Categories (Optimize First)

1. **Compute** - Largest spend, most optimization potential
2. **Database** - Often over-provisioned, expensive
3. **Data Transfer** - Hidden costs, egress fees
4. **Storage** - Grows over time, lifecycle policies help

### Low-Hanging Fruit

- **Orphaned resources**: Storage, snapshots, IPs
- **Idle compute**: Development instances running 24/7
- **Over-provisioned databases**: More capacity than needed
- **Uncompressed data**: Storage and transfer costs

### Cost Optimization Priority Matrix

| Category | Optimization Potential | Complexity | Priority |
|----------|----------------------|------------|----------|
| Compute | High | Medium | 1 |
| Data Transfer | High | Low | 2 |
| Storage | Medium | Low | 3 |
| Database | High | High | 4 |
| Observability | Medium | Medium | 5 |

---

**Use this taxonomy consistently across your organization to enable meaningful cost comparisons and optimization.**
