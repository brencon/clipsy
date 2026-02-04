#!/usr/bin/env python3
"""
Cost Analysis Engine

Scans codebase to identify cloud service usage and estimate costs.
Provides deterministic calculations based on code patterns and configurations.
"""

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ServiceUsage:
    """Represents usage of a cloud service."""
    provider: str
    service: str
    resource_type: str
    location: str  # File path where found
    line_number: int
    estimated_monthly_cost: float
    confidence: str  # "high", "medium", "low"
    notes: str


@dataclass
class CostReport:
    """Complete cost analysis report."""
    timestamp: str
    total_estimated_cost: float
    services: List[ServiceUsage]
    by_provider: Dict[str, float]
    by_category: Dict[str, float]
    recommendations: List[str]


# Cloud service patterns to search for
CLOUD_PATTERNS = {
    # AWS
    "aws": {
        "imports": [
            r"import boto3",
            r"from boto3",
            r"import aws_cdk",
            r"from aws_cdk",
            r"@aws-sdk",
        ],
        "services": {
            "ec2": [r"ec2\.Instance", r"EC2\(", r"\.run_instances\("],
            "lambda": [r"lambda\.Function", r"Lambda\(", r"\.create_function\("],
            "s3": [r"s3\.Bucket", r"S3\(", r"\.create_bucket\("],
            "rds": [r"rds\.Database", r"RDS\(", r"\.create_db_instance\("],
            "dynamodb": [r"dynamodb\.Table", r"DynamoDB\(", r"\.create_table\("],
            "cloudfront": [r"cloudfront\.Distribution", r"CloudFront\("],
            "apigateway": [r"apigateway\.RestApi", r"APIGateway\("],
            "sqs": [r"sqs\.Queue", r"SQS\(", r"\.create_queue\("],
            "sns": [r"sns\.Topic", r"SNS\(", r"\.create_topic\("],
        }
    },
    # GCP
    "gcp": {
        "imports": [
            r"from google\.cloud",
            r"import google\.cloud",
            r"@google-cloud",
        ],
        "services": {
            "compute": [r"compute_v1\.Instance", r"Compute\("],
            "functions": [r"functions_v1\.CloudFunction", r"CloudFunctions\("],
            "storage": [r"storage\.Bucket", r"Storage\("],
            "cloudsql": [r"sqladmin_v1\.DatabaseInstance"],
            "bigquery": [r"bigquery\.Client", r"BigQuery\("],
            "firestore": [r"firestore\.Client", r"Firestore\("],
            "pubsub": [r"pubsub_v1\.Topic", r"PubSub\("],
        }
    },
    # Azure
    "azure": {
        "imports": [
            r"from azure\.",
            r"import azure\.",
            r"@azure/",
        ],
        "services": {
            "vm": [r"VirtualMachine", r"compute\.VirtualMachine"],
            "functions": [r"FunctionApp", r"\.function_app"],
            "storage": [r"BlobServiceClient", r"StorageAccount"],
            "cosmosdb": [r"CosmosClient", r"cosmos_client"],
            "sql": [r"SqlServer", r"sql_server"],
        }
    },
    # Other services
    "vercel": {
        "imports": [r"vercel\.json", r"@vercel/"],
        "services": {"deployment": [r"vercel\.json"]}
    },
    "netlify": {
        "imports": [r"netlify\.toml", r"\.netlify/"],
        "services": {"deployment": [r"netlify\.toml"]}
    },
    "heroku": {
        "imports": [r"Procfile", r"heroku"],
        "services": {"dyno": [r"Procfile"]}
    },
}

# Estimated monthly costs (baseline estimates)
# These are conservative estimates for small-medium workloads
COST_ESTIMATES = {
    "aws": {
        "ec2": {"t3.micro": 8, "t3.small": 16, "t3.medium": 32, "default": 50},
        "lambda": 5,  # Per million requests
        "s3": 25,  # Per TB/month
        "rds": {"db.t3.micro": 15, "db.t3.small": 30, "default": 100},
        "dynamodb": 25,  # On-demand, light usage
        "cloudfront": 50,
        "apigateway": 10,  # Per million requests
        "sqs": 5,
        "sns": 5,
    },
    "gcp": {
        "compute": {"e2-micro": 7, "e2-small": 14, "e2-medium": 28, "default": 45},
        "functions": 5,
        "storage": 20,  # Per TB/month
        "cloudsql": {"db-f1-micro": 10, "db-g1-small": 25, "default": 90},
        "bigquery": 50,
        "firestore": 20,
        "pubsub": 5,
    },
    "azure": {
        "vm": {"B1S": 10, "B2S": 40, "default": 60},
        "functions": 5,
        "storage": 20,
        "cosmosdb": 50,
        "sql": {"Basic": 5, "Standard": 30, "default": 100},
    },
    "vercel": {"deployment": 20},
    "netlify": {"deployment": 15},
    "heroku": {"dyno": {"hobby": 7, "standard-1x": 25, "default": 50}},
}


class CostAnalyzer:
    """Analyzes codebase for cloud service usage and costs."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.services: List[ServiceUsage] = []

    def scan_file(self, file_path: Path) -> List[ServiceUsage]:
        """Scan a single file for cloud service patterns."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, PermissionError):
            return []

        findings = []

        for provider, patterns in CLOUD_PATTERNS.items():
            # Check if file uses this provider
            provider_found = False
            for import_pattern in patterns["imports"]:
                if re.search(import_pattern, content, re.IGNORECASE):
                    provider_found = True
                    break

            if not provider_found:
                continue

            # Look for specific services
            for service_name, service_patterns in patterns.get("services", {}).items():
                for pattern in service_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        # Find line number
                        line_num = content[:match.start()].count('\n') + 1

                        # Estimate cost
                        estimated_cost = self._estimate_cost(provider, service_name)

                        usage = ServiceUsage(
                            provider=provider.upper(),
                            service=service_name,
                            resource_type=self._categorize_service(service_name),
                            location=str(file_path.relative_to(self.project_root)),
                            line_number=line_num,
                            estimated_monthly_cost=estimated_cost,
                            confidence="medium",
                            notes=f"Found pattern: {pattern}"
                        )
                        findings.append(usage)

        return findings

    def _estimate_cost(self, provider: str, service: str) -> float:
        """Estimate monthly cost for a service."""
        costs = COST_ESTIMATES.get(provider, {})
        service_cost = costs.get(service, 0)

        # Handle dict costs (multiple tiers)
        if isinstance(service_cost, dict):
            return service_cost.get("default", 50)

        return service_cost if service_cost else 25  # Default estimate

    def _categorize_service(self, service: str) -> str:
        """Categorize service by type."""
        compute = ["ec2", "lambda", "functions", "compute", "vm", "dyno"]
        storage = ["s3", "storage", "bucket"]
        database = ["rds", "dynamodb", "cloudsql", "bigquery", "firestore", "cosmosdb", "sql"]
        networking = ["cloudfront", "apigateway", "cdn"]
        messaging = ["sqs", "sns", "pubsub"]

        service_lower = service.lower()
        if any(s in service_lower for s in compute):
            return "Compute"
        elif any(s in service_lower for s in storage):
            return "Storage"
        elif any(s in service_lower for s in database):
            return "Database"
        elif any(s in service_lower for s in networking):
            return "Networking"
        elif any(s in service_lower for s in messaging):
            return "Messaging"
        else:
            return "Other"

    def scan_project(self) -> None:
        """Scan entire project for cloud services."""
        # File patterns to scan
        code_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.java', '.rb', '.php', '.cs'}
        config_files = {'Procfile', 'vercel.json', 'netlify.toml', 'Dockerfile', 'docker-compose.yml'}

        # Directories to skip
        skip_dirs = {'.git', 'node_modules', 'venv', '.venv', '__pycache__', 'dist', 'build', '.next'}

        for file_path in self.project_root.rglob('*'):
            # Skip directories
            if file_path.is_dir():
                continue

            # Skip excluded directories
            if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                continue

            # Check if we should scan this file
            should_scan = (
                file_path.suffix in code_extensions or
                file_path.name in config_files
            )

            if should_scan:
                findings = self.scan_file(file_path)
                self.services.extend(findings)

    def generate_report(self) -> CostReport:
        """Generate comprehensive cost report."""
        total_cost = sum(s.estimated_monthly_cost for s in self.services)

        # Group by provider
        by_provider = {}
        for service in self.services:
            provider = service.provider
            by_provider[provider] = by_provider.get(provider, 0) + service.estimated_monthly_cost

        # Group by category
        by_category = {}
        for service in self.services:
            category = service.resource_type
            by_category[category] = by_category.get(category, 0) + service.estimated_monthly_cost

        # Generate recommendations
        recommendations = self._generate_recommendations()

        return CostReport(
            timestamp=datetime.utcnow().isoformat(),
            total_estimated_cost=round(total_cost, 2),
            services=[s for s in self.services],  # Convert to dicts for JSON
            by_provider=by_provider,
            by_category=by_category,
            recommendations=recommendations
        )

    def _generate_recommendations(self) -> List[str]:
        """Generate cost optimization recommendations."""
        recs = []

        # Check for multiple cloud providers
        providers = set(s.provider for s in self.services)
        if len(providers) > 2:
            recs.append(
                f"Multi-cloud detected ({len(providers)} providers). Consider consolidating to reduce "
                "complexity and potentially negotiate volume discounts."
            )

        # Check for expensive services
        expensive = [s for s in self.services if s.estimated_monthly_cost > 100]
        if expensive:
            recs.append(
                f"Found {len(expensive)} high-cost service(s). Review for rightsizing opportunities "
                "or consider reserved/committed pricing."
            )

        # Check for compute services
        compute_services = [s for s in self.services if s.resource_type == "Compute"]
        if compute_services:
            recs.append(
                f"Found {len(compute_services)} compute resource(s). Ensure auto-scaling is configured "
                "and consider spot/preemptible instances for fault-tolerant workloads."
            )

        # Check for storage
        storage_services = [s for s in self.services if s.resource_type == "Storage"]
        if storage_services:
            recs.append(
                f"Found {len(storage_services)} storage resource(s). Implement lifecycle policies to "
                "move infrequently accessed data to cheaper storage tiers."
            )

        if not recs:
            recs.append("No immediate optimization opportunities identified. Continue monitoring costs.")

        return recs


def main():
    parser = argparse.ArgumentParser(description="Analyze project for cloud service costs")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Root directory of the project to analyze"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file for JSON report (default: stdout)"
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="markdown",
        help="Output format"
    )

    args = parser.parse_args()

    # Run analysis
    analyzer = CostAnalyzer(args.project_root)
    print(f"Scanning project: {args.project_root}")
    analyzer.scan_project()
    print(f"Found {len(analyzer.services)} cloud service usage(s)")

    report = analyzer.generate_report()

    # Output report
    if args.format == "json":
        output = json.dumps(asdict(report), indent=2, default=str)
    else:
        output = format_markdown_report(report)

    if args.output:
        args.output.write_text(output)
        print(f"Report saved to: {args.output}")
    else:
        print("\n" + "=" * 80)
        print(output)


def format_markdown_report(report: CostReport) -> str:
    """Format report as markdown."""
    md = f"""# Cloud Cost Analysis Report

**Generated**: {report.timestamp}
**Total Estimated Monthly Cost**: ${report.total_estimated_cost:,.2f}

## Cost Summary

### By Provider
"""
    for provider, cost in sorted(report.by_provider.items(), key=lambda x: x[1], reverse=True):
        percentage = (cost / report.total_estimated_cost * 100) if report.total_estimated_cost > 0 else 0
        md += f"- **{provider}**: ${cost:,.2f} ({percentage:.1f}%)\n"

    md += "\n### By Category\n"
    for category, cost in sorted(report.by_category.items(), key=lambda x: x[1], reverse=True):
        percentage = (cost / report.total_estimated_cost * 100) if report.total_estimated_cost > 0 else 0
        md += f"- **{category}**: ${cost:,.2f} ({percentage:.1f}%)\n"

    md += "\n## Identified Services\n\n"
    md += "| Provider | Service | Category | Location | Est. Cost/Month |\n"
    md += "|----------|---------|----------|----------|----------------|\n"

    for service in sorted(report.services, key=lambda x: x.estimated_monthly_cost, reverse=True):
        md += f"| {service.provider} | {service.service} | {service.resource_type} | "
        md += f"{service.location}:{service.line_number} | ${service.estimated_monthly_cost:.2f} |\n"

    md += "\n## Recommendations\n\n"
    for i, rec in enumerate(report.recommendations, 1):
        md += f"{i}. {rec}\n\n"

    md += """
## Next Steps

1. Review identified services for accuracy
2. Obtain actual billing data for precise cost tracking
3. Implement cost allocation tags for better visibility
4. Set up billing alerts and budgets
5. Schedule quarterly cost reviews

---

*Note: Cost estimates are approximate. Actual costs depend on usage patterns, region, and specific configurations.*
"""

    return md


if __name__ == "__main__":
    main()
