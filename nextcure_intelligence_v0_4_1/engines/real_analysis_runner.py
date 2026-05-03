"""Iteration 4 orchestration: real data fetch + classification + channel insight layer."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from config.peer_channels import all_market_tickers, peer_metadata_by_ticker
from data.mock_market_data import (
    build_mock_insights,
    build_mock_kpi_cards,
    build_mock_peer_table,
    build_mock_performance,
    build_mock_technical_data,
)
from engines.channel_engine import ChannelSummary, analyze_channels
from engines.classification_engine import ClassificationResult, classify_market_position
from engines.insight_engine import build_executive_insights, build_watch_items
from engines.market_data_engine import MarketDataBundle, add_technical_indicators, fetch_market_data
from engines.relative_performance_engine import build_relative_index, build_return_table, safe_return


@dataclass(frozen=True)
class AnalysisResults:
    performance: pd.DataFrame
    peer_table: pd.DataFrame
    technicals: dict[str, pd.DataFrame]
    kpis: list[dict[str, str]]
    insights: list[str]
    data_bundle: MarketDataBundle | None
    using_real_data: bool
    return_table: pd.DataFrame | None = None
    classification: ClassificationResult | None = None
    channel_summaries: list[ChannelSummary] | None = None
    channel_table: pd.DataFrame | None = None
    watch_items: list[dict[str, str]] | None = None


def _format_delta(value: object) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    number = float(value)
    return f"{number:+.2f}%"


def _build_kpis(return_table: pd.DataFrame, failures: dict[str, str], classification: ClassificationResult) -> list[dict[str, str]]:
    nxtc_5d = safe_return(return_table, "NXTC", "5D %")
    xbi_5d = safe_return(return_table, "XBI", "5D %")
    qqq_5d = safe_return(return_table, "QQQ", "5D %")
    nxtc_30d = safe_return(return_table, "NXTC", "30D %")

    return [
        {"label": "NXTC 5D", "value": _format_delta(nxtc_5d), "caption": "Recent company movement"},
        {"label": "NXTC 30D", "value": _format_delta(nxtc_30d), "caption": "Medium-term posture"},
        {"label": "NXTC vs XBI", "value": _format_delta(classification.spread_5d_xbi), "caption": classification.nxtc_vs_xbi},
        {"label": "XBI 5D", "value": _format_delta(xbi_5d), "caption": "Biotech sector proxy"},
        {"label": "QQQ 5D", "value": _format_delta(qqq_5d), "caption": "Growth-market proxy"},
        {"label": "Data Gaps", "value": str(len(failures)), "caption": "Tickers safely skipped"},
    ]


def _build_peer_table(return_table: pd.DataFrame) -> pd.DataFrame:
    metadata = peer_metadata_by_ticker()
    rows: list[dict[str, object]] = []
    for _, row in return_table.iterrows():
        ticker = str(row["Ticker"])
        meta = metadata.get(ticker)
        if ticker in {"XBI", "QQQ"} or meta is None:
            continue
        rows.append({
            "Ticker": ticker,
            "Company": meta.company,
            "Channels": ", ".join(ch for ch in meta.channels if ch != "primary"),
            "Targets": ", ".join(meta.targets),
            "1D %": row.get("1D %"),
            "5D %": row.get("5D %"),
            "30D %": row.get("30D %"),
            "60D %": row.get("60D %"),
            "90D %": row.get("90D %"),
            "Read": meta.read_through,
        })
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values("5D %", ascending=False, na_position="last").reset_index(drop=True)


def run_real_analysis() -> AnalysisResults:
    tickers = all_market_tickers()
    bundle = fetch_market_data(tickers, period="6mo", interval="1d", min_rows=30)

    required = {"NXTC", "XBI", "QQQ"}
    if not required.issubset(bundle.prices):
        return AnalysisResults(
            performance=build_mock_performance(),
            peer_table=build_mock_peer_table(),
            technicals=build_mock_technical_data(),
            kpis=build_mock_kpi_cards(),
            insights=[
                "Live market data was not available for all required benchmarks, so the app is showing prototype data while preserving the Iteration 4 engine wiring.",
                *build_mock_insights(),
            ],
            data_bundle=bundle,
            using_real_data=False,
        )

    technicals = {ticker: add_technical_indicators(df) for ticker, df in bundle.prices.items()}
    return_table = build_return_table(bundle.prices)
    performance = build_relative_index(bundle.prices, ["NXTC", "XBI", "QQQ"])
    peer_table = _build_peer_table(return_table)
    classification = classify_market_position(return_table)
    channel_summaries, channel_table = analyze_channels(return_table)
    insights = build_executive_insights(return_table, classification, channel_summaries, bundle.failures)
    watch_items = build_watch_items(classification, channel_summaries)

    return AnalysisResults(
        performance=performance,
        peer_table=peer_table,
        technicals=technicals,
        kpis=_build_kpis(return_table, bundle.failures, classification),
        insights=insights,
        data_bundle=bundle,
        using_real_data=True,
        return_table=return_table,
        classification=classification,
        channel_summaries=channel_summaries,
        channel_table=channel_table,
        watch_items=watch_items,
    )
