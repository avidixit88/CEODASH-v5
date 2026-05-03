"""Chart builders for the Streamlit UI."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


CHART_BG = "rgba(15,23,42,.35)"
GRID = "rgba(255,255,255,.08)"
FONT = "#E2E8F0"


def _apply_dark_layout(fig: go.Figure, height: int) -> go.Figure:
    fig.update_layout(
        height=height,
        margin={"l": 20, "r": 20, "t": 35, "b": 20},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=CHART_BG,
        font={"color": FONT},
        legend={"orientation": "h", "y": 1.06, "x": 0},
    )
    fig.update_xaxes(gridcolor=GRID)
    fig.update_yaxes(gridcolor=GRID)
    return fig


def relative_performance_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for ticker in ["NXTC", "XBI", "QQQ"]:
        fig.add_trace(
            go.Scatter(
                x=df["Date"],
                y=df[ticker],
                mode="lines",
                name=ticker,
                line={"width": 3 if ticker == "NXTC" else 2},
            )
        )
    fig = _apply_dark_layout(fig, 420)
    fig.update_yaxes(title_text="Relative Performance %")
    fig.update_xaxes(title_text=None)
    return fig


def peer_bar_chart(peer_df: pd.DataFrame) -> go.Figure:
    view = peer_df.sort_values("5D %", ascending=True).tail(12)
    fig = go.Figure(
        go.Bar(
            x=view["5D %"],
            y=view["Ticker"],
            orientation="h",
            text=view["Read"],
            textposition="auto",
        )
    )
    fig = _apply_dark_layout(fig, 420)
    fig.update_xaxes(title_text="5D Performance %")
    fig.update_yaxes(title_text=None, gridcolor="rgba(255,255,255,.04)")
    return fig


def technical_stock_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    """Six-month stock technical panel: price/EMAs, RSI, MACD."""
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.055,
        row_heights=[0.58, 0.20, 0.22],
        subplot_titles=(f"{ticker} Six-Month Price Structure", "RSI 14", "MACD"),
    )
    fig.add_trace(go.Candlestick(
        x=df["Date"], open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="OHLC"
    ), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["EMA20"], mode="lines", name="EMA 20", line={"width": 1.8}), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["EMA50"], mode="lines", name="EMA 50", line={"width": 1.8}), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["RSI14"], mode="lines", name="RSI 14", line={"width": 2}), row=2, col=1)
    fig.add_hline(y=70, line_dash="dot", opacity=0.35, row=2, col=1)
    fig.add_hline(y=50, line_dash="dot", opacity=0.20, row=2, col=1)
    fig.add_hline(y=30, line_dash="dot", opacity=0.35, row=2, col=1)
    fig.add_trace(go.Bar(x=df["Date"], y=df["MACD_Hist"], name="MACD Hist", opacity=0.55), row=3, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["MACD"], mode="lines", name="MACD", line={"width": 2}), row=3, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["MACD_Signal"], mode="lines", name="Signal", line={"width": 1.6}), row=3, col=1)
    fig.update_layout(
        height=760,
        margin={"l": 20, "r": 20, "t": 55, "b": 25},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=CHART_BG,
        font={"color": FONT},
        legend={"orientation": "h", "y": 1.03, "x": 0},
        xaxis_rangeslider_visible=False,
    )
    fig.update_xaxes(gridcolor=GRID)
    fig.update_yaxes(gridcolor=GRID)
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="RSI", range=[0, 100], row=2, col=1)
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    return fig


def channel_momentum_chart(channel_df: pd.DataFrame) -> go.Figure:
    if channel_df.empty:
        return _apply_dark_layout(go.Figure(), 420)
    view = channel_df.sort_values("30D Avg %", ascending=True, na_position="first")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=view["30D Avg %"], y=view["Channel"], orientation="h", name="30D Avg %"))
    fig.add_trace(go.Scatter(x=view["5D Avg %"], y=view["Channel"], mode="markers", name="5D Avg %", marker={"size": 11}))
    fig = _apply_dark_layout(fig, 440)
    fig.update_xaxes(title_text="Channel Performance %")
    fig.update_yaxes(title_text=None, gridcolor="rgba(255,255,255,.04)")
    return fig
