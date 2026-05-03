"""CEO-level insight generation from classifications and channel analytics."""

from __future__ import annotations

import pandas as pd

from engines.channel_engine import ChannelSummary
from engines.classification_engine import ClassificationResult
from engines.relative_performance_engine import safe_return


def _fmt(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:+.2f}%"


def build_executive_insights(
    return_table: pd.DataFrame,
    classification: ClassificationResult,
    channels: list[ChannelSummary],
    failures: dict[str, str],
) -> list[str]:
    insights: list[str] = []

    nxtc_5d = safe_return(return_table, "NXTC", "5D %")
    xbi_5d = safe_return(return_table, "XBI", "5D %")
    qqq_5d = safe_return(return_table, "QQQ", "5D %")
    nxtc_30d = safe_return(return_table, "NXTC", "30D %")
    nxtc_90d = safe_return(return_table, "NXTC", "90D %")

    if nxtc_5d is not None and xbi_5d is not None:
        insights.append(
            f"NXTC is {classification.nxtc_vs_xbi.lower()} XBI over 5D "
            f"({_fmt(classification.spread_5d_xbi)} spread), with the current driver classified as {classification.driver.lower()}."
        )

    if nxtc_30d is not None and classification.spread_30d_xbi is not None:
        insights.append(
            f"The 30D read shows NXTC at {_fmt(nxtc_30d)} and {_fmt(classification.spread_30d_xbi)} versus XBI, "
            f"which frames the medium-term posture as {classification.medium_term_state.lower()}."
        )

    if nxtc_90d is not None and classification.spread_90d_xbi is not None:
        insights.append(
            f"The quarterly view shows NXTC at {_fmt(nxtc_90d)} over 90D and {_fmt(classification.spread_90d_xbi)} versus XBI, "
            f"classifying the quarter-like posture as {classification.quarterly_state.lower()}."
        )

    if xbi_5d is not None and qqq_5d is not None:
        spread = xbi_5d - qqq_5d
        insights.append(
            f"The market regime is {classification.market_regime.lower()}: XBI is {_fmt(spread)} versus QQQ over 5D, "
            "which helps separate biotech-specific appetite from broader growth-market movement."
        )

    # Prioritize direct ADC / ovarian lanes for the CEO readout.
    channel_map = {c.channel: c for c in channels}
    for key in ["cdh6_ovarian_adc", "b7h4_adc", "adc_capital_flow", "ovarian_cancer"]:
        channel = channel_map.get(key)
        if channel is None:
            continue
        insights.append(
            f"{channel.label} is classified as {channel.momentum_label.lower()} with {channel.capital_flow.lower()} "
            f"(5D avg {_fmt(channel.avg_5d)}, 30D avg {_fmt(channel.avg_30d)}, quarterly/90D avg {_fmt(channel.avg_90d)}). "
            f"Best 5D contributor: {channel.best_ticker or 'N/A'}."
        )

    if failures:
        insights.append(
            f"Data quality note: {len(failures)} ticker(s) were unavailable or incomplete and were skipped safely without breaking the dashboard."
        )

    return insights or ["Real market data loaded, but the intelligence layer had insufficient benchmark history to produce a complete readout."]


def build_watch_items(classification: ClassificationResult, channels: list[ChannelSummary]) -> list[dict[str, str]]:
    direct = {c.channel: c for c in channels}
    watch_items = [
        {"label": "Market Regime", "value": classification.market_regime, "caption": "XBI vs QQQ context"},
        {"label": "NXTC Driver", "value": classification.driver, "caption": "Sector vs stock-specific"},
        {"label": "Short-Term State", "value": classification.short_term_state, "caption": "5D vs 30D spread"},
        {"label": "Quarterly View", "value": classification.quarterly_state, "caption": "90D vs XBI"},
    ]
    adc = direct.get("adc_capital_flow")
    ovarian = direct.get("ovarian_cancer")
    if adc:
        watch_items.append({"label": "ADC Flow", "value": adc.capital_flow, "caption": f"30D avg {_fmt(adc.avg_30d)}"})
    if ovarian:
        watch_items.append({"label": "Ovarian Lane", "value": ovarian.momentum_label, "caption": f"30D avg {_fmt(ovarian.avg_30d)}"})
    return watch_items
