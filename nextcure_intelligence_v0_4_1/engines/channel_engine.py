"""Channel-level analysis for direct peers, ADC landscape, and side-channel baskets."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

import pandas as pd

from config.peer_channels import PEER_COMPANIES
from engines.relative_performance_engine import safe_return

CHANNEL_LABELS = {
    "cdh6_ovarian_adc": "CDH6 / Ovarian ADC",
    "b7h4_adc": "B7-H4 ADC",
    "ovarian_cancer": "Ovarian Cancer",
    "adc_capital_flow": "ADC Capital Flow",
    "small_cap_oncology": "Small-Cap Oncology",
    "alzheimers_partnering_channel": "Alzheimer's Side Channel",
    "bone_disease_partnering_channel": "Bone Disease Side Channel",
}

CHANNEL_ORDER = [
    "cdh6_ovarian_adc",
    "b7h4_adc",
    "ovarian_cancer",
    "adc_capital_flow",
    "small_cap_oncology",
    "alzheimers_partnering_channel",
    "bone_disease_partnering_channel",
]


@dataclass(frozen=True)
class ChannelSummary:
    channel: str
    label: str
    tickers: tuple[str, ...]
    avg_5d: float | None
    avg_30d: float | None
    avg_60d: float | None
    avg_90d: float | None
    momentum_label: str
    capital_flow: str
    best_ticker: str | None
    worst_ticker: str | None


def _avg(values: list[float | None]) -> float | None:
    clean = [v for v in values if v is not None and not pd.isna(v)]
    return round(mean(clean), 2) if clean else None


def _label(avg_5d: float | None, avg_30d: float | None) -> tuple[str, str]:
    if avg_5d is None and avg_30d is None:
        return "Unavailable", "Unknown"
    short = avg_5d if avg_5d is not None else 0
    medium = avg_30d if avg_30d is not None else short
    blended = (short * 0.6) + (medium * 0.4)
    if blended > 5:
        return "Strong", "Inflow"
    if blended > 1.5:
        return "Constructive", "Selective inflow"
    if blended < -5:
        return "Weak", "Outflow"
    if blended < -1.5:
        return "Soft", "Selective outflow"
    return "Neutral", "Balanced"


def analyze_channels(return_table: pd.DataFrame) -> tuple[list[ChannelSummary], pd.DataFrame]:
    summaries: list[ChannelSummary] = []
    table_rows: list[dict[str, object]] = []

    for channel in CHANNEL_ORDER:
        tickers = sorted({company.ticker for company in PEER_COMPANIES if channel in company.channels and company.ticker != "NXTC"})
        if not tickers:
            continue
        rows = []
        for ticker in tickers:
            r5 = safe_return(return_table, ticker, "5D %")
            r30 = safe_return(return_table, ticker, "30D %")
            r60 = safe_return(return_table, ticker, "60D %")
            r90 = safe_return(return_table, ticker, "90D %")
            rows.append((ticker, r5, r30, r60, r90))

        avg_5d = _avg([r[1] for r in rows])
        avg_30d = _avg([r[2] for r in rows])
        avg_60d = _avg([r[3] for r in rows])
        avg_90d = _avg([r[4] for r in rows])
        momentum, flow = _label(avg_5d, avg_30d)

        ranked = [r for r in rows if r[1] is not None]
        ranked.sort(key=lambda x: x[1], reverse=True)
        best = ranked[0][0] if ranked else None
        worst = ranked[-1][0] if ranked else None

        label = CHANNEL_LABELS.get(channel, channel)
        summaries.append(ChannelSummary(channel, label, tuple(tickers), avg_5d, avg_30d, avg_60d, avg_90d, momentum, flow, best, worst))
        table_rows.append({
            "Channel": label,
            "Tickers": ", ".join(tickers),
            "5D Avg %": avg_5d,
            "30D Avg %": avg_30d,
            "60D Avg %": avg_60d,
            "90D Avg %": avg_90d,
            "Momentum": momentum,
            "Capital Flow": flow,
            "Best 5D": best or "N/A",
            "Weakest 5D": worst or "N/A",
        })

    return summaries, pd.DataFrame(table_rows)
