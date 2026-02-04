#!/usr/bin/env python3
"""
Cost Forecasting Tool

Projects future cloud costs based on historical trends and growth assumptions.
"""

import argparse
import json
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import math


@dataclass
class ForecastPeriod:
    """Forecast for a single period."""
    month: str
    base_cost: float
    growth_adjustment: float
    projected_cost: float
    confidence: str  # high, medium, low


@dataclass
class CostForecast:
    """Complete cost forecast."""
    start_date: str
    periods: int
    base_monthly_cost: float
    growth_rate: float
    forecast_periods: List[ForecastPeriod]
    total_projected: float
    assumptions: List[str]


class CostForecaster:
    """Forecast future costs based on parameters."""

    def __init__(
        self,
        base_cost: float,
        growth_rate: float = 0.0,
        seasonal_factors: Optional[Dict[int, float]] = None
    ):
        """
        Initialize forecaster.

        Args:
            base_cost: Current monthly cost baseline
            growth_rate: Monthly growth rate (e.g., 0.10 for 10%)
            seasonal_factors: Optional dict of month -> multiplier for seasonality
        """
        self.base_cost = base_cost
        self.growth_rate = growth_rate
        self.seasonal_factors = seasonal_factors or {}

    def forecast(self, months: int, start_date: Optional[datetime] = None) -> CostForecast:
        """Generate cost forecast."""
        if start_date is None:
            start_date = datetime.now()

        forecast_periods = []
        cumulative_cost = 0

        for i in range(months):
            # Calculate month
            forecast_date = start_date + timedelta(days=30 * i)
            month_str = forecast_date.strftime('%Y-%m')
            month_num = forecast_date.month

            # Calculate base with growth
            # Compound growth: base * (1 + rate)^month
            growth_multiplier = (1 + self.growth_rate) ** i
            base_with_growth = self.base_cost * growth_multiplier

            # Apply seasonal factors
            seasonal_factor = self.seasonal_factors.get(month_num, 1.0)
            projected = base_with_growth * seasonal_factor

            # Determine confidence
            # Confidence decreases over time
            if i < 3:
                confidence = "high"
            elif i < 6:
                confidence = "medium"
            else:
                confidence = "low"

            period = ForecastPeriod(
                month=month_str,
                base_cost=round(base_with_growth, 2),
                growth_adjustment=round((growth_multiplier - 1) * 100, 2),
                projected_cost=round(projected, 2),
                confidence=confidence
            )
            forecast_periods.append(period)
            cumulative_cost += projected

        # Generate assumptions
        assumptions = self._generate_assumptions()

        return CostForecast(
            start_date=start_date.strftime('%Y-%m-%d'),
            periods=months,
            base_monthly_cost=self.base_cost,
            growth_rate=self.growth_rate,
            forecast_periods=forecast_periods,
            total_projected=round(cumulative_cost, 2),
            assumptions=assumptions
        )

    def _generate_assumptions(self) -> List[str]:
        """Generate list of forecast assumptions."""
        assumptions = [
            f"Base monthly cost: ${self.base_cost:,.2f}",
            f"Monthly growth rate: {self.growth_rate * 100:.1f}%"
        ]

        if self.growth_rate > 0:
            assumptions.append(
                "Growth is modeled as compound (accelerating) rather than linear"
            )

        if self.seasonal_factors:
            assumptions.append(
                f"Seasonal adjustments applied for {len(self.seasonal_factors)} months"
            )
        else:
            assumptions.append("No seasonal variations assumed")

        assumptions.extend([
            "Forecast does not account for one-time costs or credits",
            "Assumes no major architectural changes",
            "Pricing assumed to remain constant (no provider price changes)",
            "Confidence decreases with forecast horizon"
        ])

        return assumptions

    @staticmethod
    def estimate_growth_from_history(historical_costs: List[float]) -> float:
        """
        Estimate growth rate from historical data.

        Args:
            historical_costs: List of monthly costs (oldest to newest)

        Returns:
            Estimated monthly growth rate
        """
        if len(historical_costs) < 2:
            return 0.0

        # Use compound annual growth rate (CAGR) formula
        # CAGR = (End Value / Start Value)^(1 / num_periods) - 1
        start = historical_costs[0]
        end = historical_costs[-1]
        periods = len(historical_costs) - 1

        if start <= 0:
            return 0.0

        cagr = (end / start) ** (1 / periods) - 1
        return cagr


def format_markdown_forecast(forecast: CostForecast) -> str:
    """Format forecast as markdown."""
    md = f"""# Cloud Cost Forecast

**Forecast Start**: {forecast.start_date}
**Periods**: {forecast.periods} months
**Base Monthly Cost**: ${forecast.base_monthly_cost:,.2f}
**Growth Rate**: {forecast.growth_rate * 100:.1f}% per month
**Total Projected ({forecast.periods} months)**: ${forecast.total_projected:,.2f}

## Monthly Projections

| Month | Base Cost | Growth | Projected | Confidence |
|-------|-----------|--------|-----------|------------|
"""

    for period in forecast.forecast_periods:
        md += f"| {period.month} | ${period.base_cost:,.2f} | "
        md += f"+{period.growth_adjustment:.1f}% | ${period.projected_cost:,.2f} | "
        md += f"{period.confidence.title()} |\n"

    # Calculate summary stats
    avg_monthly = forecast.total_projected / forecast.periods
    first_month = forecast.forecast_periods[0].projected_cost
    last_month = forecast.forecast_periods[-1].projected_cost
    total_growth = ((last_month / first_month) - 1) * 100 if first_month > 0 else 0

    md += f"""
## Summary Statistics

- **Average Monthly Cost**: ${avg_monthly:,.2f}
- **First Month**: ${first_month:,.2f}
- **Last Month**: ${last_month:,.2f}
- **Total Growth**: {total_growth:+.1f}%

## Cost Progression

"""
    # Simple ASCII chart
    max_cost = max(p.projected_cost for p in forecast.forecast_periods)
    for period in forecast.forecast_periods:
        bar_length = int((period.projected_cost / max_cost) * 40)
        bar = "█" * bar_length
        md += f"{period.month}: {bar} ${period.projected_cost:,.2f}\n"

    md += "\n## Assumptions\n\n"
    for assumption in forecast.assumptions:
        md += f"- {assumption}\n"

    md += """
## Recommendations

1. **Budget Planning**: Set monthly budget alerts at 80% and 100% of projected costs
2. **Cost Reviews**: Schedule monthly reviews to compare actual vs. projected
3. **Optimization**: If growth exceeds projections, prioritize cost optimization
4. **Reserved Capacity**: Consider reserved instances/committed use for predictable workloads
5. **Monitoring**: Implement automated cost anomaly detection

---

*Note: Forecasts are estimates based on stated assumptions. Actual costs may vary.*
"""

    return md


def main():
    parser = argparse.ArgumentParser(description="Forecast cloud costs")
    parser.add_argument(
        "--base-cost",
        type=float,
        required=True,
        help="Current monthly cost baseline"
    )
    parser.add_argument(
        "--months",
        type=int,
        default=6,
        help="Number of months to forecast (default: 6)"
    )
    parser.add_argument(
        "--growth-rate",
        type=float,
        default=0.0,
        help="Monthly growth rate as decimal (e.g., 0.10 for 10%%)"
    )
    parser.add_argument(
        "--seasonal",
        type=str,
        help="JSON dict of seasonal factors, e.g., '{\"12\": 1.5, \"1\": 0.8}'"
    )
    parser.add_argument(
        "--historical",
        type=str,
        help="JSON array of historical costs to estimate growth rate"
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

    # Parse optional inputs
    seasonal_factors = None
    if args.seasonal:
        try:
            seasonal_factors = {int(k): float(v) for k, v in json.loads(args.seasonal).items()}
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing seasonal factors: {e}")
            return 1

    # Estimate growth from historical data if provided
    growth_rate = args.growth_rate
    if args.historical:
        try:
            historical = json.loads(args.historical)
            estimated_growth = CostForecaster.estimate_growth_from_history(historical)
            print(f"Estimated growth rate from historical data: {estimated_growth * 100:.2f}%")
            growth_rate = estimated_growth
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing historical data: {e}")
            return 1

    # Create forecast
    forecaster = CostForecaster(
        base_cost=args.base_cost,
        growth_rate=growth_rate,
        seasonal_factors=seasonal_factors
    )

    forecast = forecaster.forecast(months=args.months)

    # Output
    if args.format == "json":
        output = json.dumps(asdict(forecast), indent=2)
    else:
        output = format_markdown_forecast(forecast)

    if args.output:
        args.output.write_text(output)
        print(f"Forecast saved to: {args.output}")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    from pathlib import Path
    exit(main())
