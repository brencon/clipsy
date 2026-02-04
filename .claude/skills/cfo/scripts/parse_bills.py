#!/usr/bin/env python3
"""
Cloud Billing Parser

Parses cloud billing data from CSV/JSON exports for detailed cost analysis.
Supports AWS Cost and Usage Reports, GCP billing exports, and Azure cost exports.
"""

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict


@dataclass
class BillingRecord:
    """Represents a single billing line item."""
    date: str
    provider: str
    service: str
    resource_id: Optional[str]
    region: Optional[str]
    cost: float
    usage_amount: float
    usage_unit: str
    tags: Dict[str, str]


@dataclass
class BillingAnalysis:
    """Complete billing analysis."""
    period_start: str
    period_end: str
    total_cost: float
    record_count: int
    by_service: Dict[str, float]
    by_region: Dict[str, float]
    by_date: Dict[str, float]
    top_resources: List[Dict]
    trends: Dict[str, any]


class BillingParser:
    """Parse cloud billing exports."""

    def __init__(self):
        self.records: List[BillingRecord] = []

    def parse_aws_csv(self, file_path: Path) -> None:
        """Parse AWS Cost and Usage Report CSV."""
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # AWS CUR standard fields
                record = BillingRecord(
                    date=row.get('lineItem/UsageStartDate', ''),
                    provider='AWS',
                    service=row.get('lineItem/ProductCode', 'Unknown'),
                    resource_id=row.get('lineItem/ResourceId'),
                    region=row.get('product/region'),
                    cost=float(row.get('lineItem/UnblendedCost', 0)),
                    usage_amount=float(row.get('lineItem/UsageAmount', 0)),
                    usage_unit=row.get('lineItem/UsageType', ''),
                    tags=self._parse_tags(row)
                )
                self.records.append(record)

    def parse_gcp_json(self, file_path: Path) -> None:
        """Parse GCP billing export JSON."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # Handle both single object and array
            items = data if isinstance(data, list) else [data]

            for item in items:
                record = BillingRecord(
                    date=item.get('usage_start_time', ''),
                    provider='GCP',
                    service=item.get('service', {}).get('description', 'Unknown'),
                    resource_id=item.get('resource', {}).get('name'),
                    region=item.get('location', {}).get('region'),
                    cost=float(item.get('cost', 0)),
                    usage_amount=float(item.get('usage', {}).get('amount', 0)),
                    usage_unit=item.get('usage', {}).get('unit', ''),
                    tags=item.get('labels', {})
                )
                self.records.append(record)

    def parse_azure_csv(self, file_path: Path) -> None:
        """Parse Azure cost export CSV."""
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                record = BillingRecord(
                    date=row.get('Date', ''),
                    provider='Azure',
                    service=row.get('MeterCategory', 'Unknown'),
                    resource_id=row.get('ResourceId'),
                    region=row.get('ResourceLocation'),
                    cost=float(row.get('Cost', 0) or row.get('CostInBillingCurrency', 0)),
                    usage_amount=float(row.get('Quantity', 0)),
                    usage_unit=row.get('UnitOfMeasure', ''),
                    tags=self._parse_azure_tags(row)
                )
                self.records.append(record)

    def _parse_tags(self, row: Dict) -> Dict[str, str]:
        """Parse AWS tags from row."""
        tags = {}
        for key, value in row.items():
            if key.startswith('resourceTags/user:'):
                tag_name = key.replace('resourceTags/user:', '')
                tags[tag_name] = value
        return tags

    def _parse_azure_tags(self, row: Dict) -> Dict[str, str]:
        """Parse Azure tags from row."""
        tags_str = row.get('Tags', '{}')
        try:
            return json.loads(tags_str) if tags_str else {}
        except json.JSONDecodeError:
            return {}

    def analyze(self) -> BillingAnalysis:
        """Analyze billing records."""
        if not self.records:
            return BillingAnalysis(
                period_start='',
                period_end='',
                total_cost=0,
                record_count=0,
                by_service={},
                by_region={},
                by_date={},
                top_resources=[],
                trends={}
            )

        # Calculate aggregations
        total_cost = sum(r.cost for r in self.records)

        by_service = defaultdict(float)
        by_region = defaultdict(float)
        by_date = defaultdict(float)
        by_resource = defaultdict(float)

        dates = []
        for record in self.records:
            by_service[record.service] += record.cost
            if record.region:
                by_region[record.region] += record.cost
            if record.date:
                date_key = record.date.split('T')[0]  # Just date, no time
                by_date[date_key] += record.cost
                dates.append(record.date)
            if record.resource_id:
                by_resource[record.resource_id] += record.cost

        # Get period
        period_start = min(dates) if dates else ''
        period_end = max(dates) if dates else ''

        # Top resources
        top_resources = [
            {"resource_id": rid, "cost": cost}
            for rid, cost in sorted(by_resource.items(), key=lambda x: x[1], reverse=True)[:10]
        ]

        # Calculate trends
        trends = self._calculate_trends(by_date)

        return BillingAnalysis(
            period_start=period_start,
            period_end=period_end,
            total_cost=round(total_cost, 2),
            record_count=len(self.records),
            by_service=dict(by_service),
            by_region=dict(by_region),
            by_date=dict(by_date),
            top_resources=top_resources,
            trends=trends
        )

    def _calculate_trends(self, by_date: Dict[str, float]) -> Dict:
        """Calculate cost trends."""
        if len(by_date) < 2:
            return {"trend": "insufficient_data"}

        sorted_dates = sorted(by_date.items())
        costs = [cost for _, cost in sorted_dates]

        # Calculate basic trend
        first_half = sum(costs[:len(costs)//2])
        second_half = sum(costs[len(costs)//2:])

        if first_half > 0:
            change_pct = ((second_half - first_half) / first_half) * 100
        else:
            change_pct = 0

        # Determine trend
        if abs(change_pct) < 5:
            trend = "stable"
        elif change_pct > 0:
            trend = "increasing"
        else:
            trend = "decreasing"

        return {
            "trend": trend,
            "change_percentage": round(change_pct, 2),
            "average_daily_cost": round(sum(costs) / len(costs), 2),
            "peak_day": max(sorted_dates, key=lambda x: x[1])[0],
            "peak_cost": max(costs)
        }


def format_markdown_analysis(analysis: BillingAnalysis) -> str:
    """Format analysis as markdown report."""
    md = f"""# Cloud Billing Analysis

**Period**: {analysis.period_start} to {analysis.period_end}
**Total Cost**: ${analysis.total_cost:,.2f}
**Line Items**: {analysis.record_count:,}

## Cost Trends

**Trend**: {analysis.trends.get('trend', 'N/A').title()}
**Change**: {analysis.trends.get('change_percentage', 0):+.1f}%
**Average Daily Cost**: ${analysis.trends.get('average_daily_cost', 0):,.2f}
**Peak Day**: {analysis.trends.get('peak_day', 'N/A')} (${analysis.trends.get('peak_cost', 0):,.2f})

## Cost Breakdown

### By Service
"""

    # Sort services by cost
    sorted_services = sorted(analysis.by_service.items(), key=lambda x: x[1], reverse=True)
    for service, cost in sorted_services[:10]:
        pct = (cost / analysis.total_cost * 100) if analysis.total_cost > 0 else 0
        md += f"- **{service}**: ${cost:,.2f} ({pct:.1f}%)\n"

    if len(sorted_services) > 10:
        md += f"\n*...and {len(sorted_services) - 10} more services*\n"

    md += "\n### By Region\n"
    sorted_regions = sorted(analysis.by_region.items(), key=lambda x: x[1], reverse=True)
    for region, cost in sorted_regions[:10]:
        pct = (cost / analysis.total_cost * 100) if analysis.total_cost > 0 else 0
        md += f"- **{region}**: ${cost:,.2f} ({pct:.1f}%)\n"

    md += "\n### Top 10 Resources by Cost\n\n"
    md += "| Resource ID | Cost |\n"
    md += "|-------------|------|\n"
    for resource in analysis.top_resources:
        rid = resource['resource_id']
        # Truncate long resource IDs
        if len(rid) > 50:
            rid = rid[:47] + "..."
        md += f"| {rid} | ${resource['cost']:,.2f} |\n"

    md += "\n## Daily Cost Trend\n\n"
    sorted_dates = sorted(analysis.by_date.items())
    if len(sorted_dates) <= 31:  # Show all if <= 1 month
        for date, cost in sorted_dates:
            md += f"- {date}: ${cost:,.2f}\n"
    else:  # Show weekly summary
        md += "*Showing weekly summary (too many days to display)*\n\n"
        # Group by week
        # (Simplified - just show first and last week)
        md += f"- First week avg: ${sum(c for d, c in sorted_dates[:7]) / 7:,.2f}\n"
        md += f"- Last week avg: ${sum(c for d, c in sorted_dates[-7:]) / 7:,.2f}\n"

    return md


def main():
    parser = argparse.ArgumentParser(description="Parse cloud billing data")
    parser.add_argument(
        "--file",
        type=Path,
        required=True,
        help="Billing export file (CSV or JSON)"
    )
    parser.add_argument(
        "--provider",
        choices=["aws", "gcp", "azure", "auto"],
        default="auto",
        help="Cloud provider (auto-detect by default)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file for report (default: stdout)"
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="markdown",
        help="Output format"
    )

    args = parser.parse_args()

    if not args.file.exists():
        print(f"Error: File not found: {args.file}")
        return 1

    # Auto-detect provider if needed
    provider = args.provider
    if provider == "auto":
        if args.file.suffix == '.json':
            provider = "gcp"
        elif 'aws' in args.file.name.lower():
            provider = "aws"
        elif 'azure' in args.file.name.lower():
            provider = "azure"
        else:
            print("Could not auto-detect provider. Please specify --provider")
            return 1

    # Parse billing data
    billing = BillingParser()
    print(f"Parsing {provider.upper()} billing data from: {args.file}")

    try:
        if provider == "aws":
            billing.parse_aws_csv(args.file)
        elif provider == "gcp":
            billing.parse_gcp_json(args.file)
        elif provider == "azure":
            billing.parse_azure_csv(args.file)
    except Exception as e:
        print(f"Error parsing file: {e}")
        return 1

    print(f"Parsed {len(billing.records)} billing records")

    # Analyze
    analysis = billing.analyze()

    # Output
    if args.format == "json":
        output = json.dumps(asdict(analysis), indent=2, default=str)
    else:
        output = format_markdown_analysis(analysis)

    if args.output:
        args.output.write_text(output)
        print(f"Report saved to: {args.output}")
    else:
        print("\n" + "=" * 80)
        print(output)

    return 0


if __name__ == "__main__":
    exit(main())
