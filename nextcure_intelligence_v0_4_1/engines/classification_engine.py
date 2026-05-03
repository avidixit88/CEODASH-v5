"""Classification layer for CEO-readable market positioning labels."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from engines.relative_performance_engine import safe_return


@dataclass(frozen=True)
class ClassificationResult:
    market_regime: str
    nxtc_vs_xbi: str
    nxtc_vs_qqq: str
    driver: str
    short_term_state: str
    medium_term_state: str
    quarterly_state: str
    spread_5d_xbi: float | None
    spread_30d_xbi: float | None
    spread_60d_xbi: float | None
    spread_90d_xbi: float | None


def _spread(return_table: pd.DataFrame, a: str, b: str, window: str) -> float | None:
    av = safe_return(return_table, a, window)
    bv = safe_return(return_table, b, window)
    if av is None or bv is None:
        return None
    return av - bv


def _classify_spread(spread: float | None, threshold: float = 3.0) -> str:
    if spread is None:
        return "Unavailable"
    if spread > threshold:
        return "Outperforming"
    if spread < -threshold:
        return "Underperforming"
    return "Tracking"


def _classify_market_regime(xbi_5d: float | None, qqq_5d: float | None, xbi_30d: float | None) -> str:
    if xbi_5d is None or qqq_5d is None:
        return "Market read unavailable"
    if xbi_5d > 2 and xbi_5d - qqq_5d > 2:
        return "Biotech risk-on"
    if xbi_5d < -2 and xbi_5d - qqq_5d < -2:
        return "Biotech risk-off"
    if xbi_30d is not None and xbi_30d > 5:
        return "Constructive biotech tape"
    if xbi_30d is not None and xbi_30d < -5:
        return "Weak biotech tape"
    return "Mixed / neutral biotech tape"


def _driver(spread_5d: float | None, spread_30d: float | None) -> str:
    if spread_5d is None:
        return "Driver unavailable"
    if abs(spread_5d) <= 1.5 and (spread_30d is None or abs(spread_30d) <= 3):
        return "Mostly sector-driven"
    if spread_5d > 3 or (spread_30d is not None and spread_30d > 5):
        return "Stock-specific strength"
    if spread_5d < -3 or (spread_30d is not None and spread_30d < -5):
        return "Stock-specific weakness"
    return "Mixed sector + stock-specific movement"


def _trend_state(short_spread: float | None, medium_spreads: list[float | None]) -> str:
    valid = [x for x in medium_spreads if x is not None]
    if short_spread is None or not valid:
        return "Unavailable"
    avg_medium = sum(valid) / len(valid)
    if short_spread > 3 and avg_medium > 3:
        return "Improving and persistent"
    if short_spread > 3 and avg_medium <= 0:
        return "Short-term rebound"
    if short_spread < -3 and avg_medium < -3:
        return "Weak and persistent"
    if short_spread < -3 and avg_medium >= 0:
        return "Short-term pullback"
    return "Balanced / tracking"


def _quarterly_state(spread_90d: float | None, nxtc_90d: float | None, xbi_90d: float | None) -> str:
    """CEO-friendly 90-trading-day posture, roughly one quarter of market behavior."""
    if spread_90d is None or nxtc_90d is None or xbi_90d is None:
        return "Quarterly read unavailable"
    if spread_90d > 7 and nxtc_90d > 0:
        return "Quarterly leadership"
    if spread_90d > 3:
        return "Quarterly outperformance"
    if spread_90d < -7 and nxtc_90d < 0:
        return "Quarterly pressure"
    if spread_90d < -3:
        return "Quarterly underperformance"
    return "Quarterly tracking"


def classify_market_position(return_table: pd.DataFrame) -> ClassificationResult:
    xbi_5d = safe_return(return_table, "XBI", "5D %")
    qqq_5d = safe_return(return_table, "QQQ", "5D %")
    xbi_30d = safe_return(return_table, "XBI", "30D %")

    spread_5d = _spread(return_table, "NXTC", "XBI", "5D %")
    spread_30d = _spread(return_table, "NXTC", "XBI", "30D %")
    spread_60d = _spread(return_table, "NXTC", "XBI", "60D %")
    spread_90d = _spread(return_table, "NXTC", "XBI", "90D %")
    qqq_spread_5d = _spread(return_table, "NXTC", "QQQ", "5D %")
    nxtc_90d = safe_return(return_table, "NXTC", "90D %")
    xbi_90d = safe_return(return_table, "XBI", "90D %")

    return ClassificationResult(
        market_regime=_classify_market_regime(xbi_5d, qqq_5d, xbi_30d),
        nxtc_vs_xbi=_classify_spread(spread_5d),
        nxtc_vs_qqq=_classify_spread(qqq_spread_5d),
        driver=_driver(spread_5d, spread_30d),
        short_term_state=_trend_state(spread_5d, [spread_30d]),
        medium_term_state=_trend_state(spread_30d, [spread_60d, spread_90d]),
        quarterly_state=_quarterly_state(spread_90d, nxtc_90d, xbi_90d),
        spread_5d_xbi=spread_5d,
        spread_30d_xbi=spread_30d,
        spread_60d_xbi=spread_60d,
        spread_90d_xbi=spread_90d,
    )
