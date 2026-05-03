"""Visual styling for the NextCure Intelligence System."""

from __future__ import annotations

import streamlit as st


def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background: radial-gradient(circle at top left, rgba(124, 58, 237, 0.25), transparent 28%),
                        radial-gradient(circle at top right, rgba(14, 165, 233, 0.15), transparent 26%),
                        linear-gradient(135deg, #080B18 0%, #111827 44%, #1E1B4B 100%);
            color: #F8FAFC;
        }
        [data-testid="stHeader"] { background: rgba(8, 11, 24, 0); }
        [data-testid="stToolbar"] { display: none; }
        .block-container { max-width: 1180px; padding-top: 2rem; }
        .hero {
            padding: 2.2rem 2.4rem;
            border: 1px solid rgba(255,255,255,.12);
            background: rgba(15, 23, 42, .74);
            border-radius: 28px;
            box-shadow: 0 28px 80px rgba(0,0,0,.35);
            backdrop-filter: blur(18px);
        }
        .eyebrow { color: #A78BFA; font-size: .78rem; letter-spacing: .18em; text-transform: uppercase; font-weight: 700; }
        .hero h1 { font-size: 3.1rem; line-height: 1.02; margin: .55rem 0; color: #FFFFFF; }
        .hero p { color: #CBD5E1; font-size: 1.05rem; max-width: 760px; }
        .status-pill {
            display: inline-flex; align-items: center; gap: .45rem; padding: .42rem .72rem;
            border-radius: 999px; border: 1px solid rgba(167,139,250,.35);
            color: #EDE9FE; background: rgba(124,58,237,.12); font-size: .82rem; font-weight: 650;
        }
        .card {
            padding: 1.15rem 1.2rem; border: 1px solid rgba(255,255,255,.10);
            background: rgba(15, 23, 42, .68); border-radius: 22px;
            box-shadow: 0 18px 50px rgba(0,0,0,.22); height: 100%;
        }
        .metric-label { color: #94A3B8; font-size: .82rem; }
        .metric-value { color: #FFFFFF; font-size: 1.65rem; font-weight: 800; margin-top: .25rem; }
        .section-title { font-size: 1.25rem; font-weight: 800; color: #FFFFFF; margin: 1rem 0 .4rem; }
        .muted { color: #94A3B8; }
        .insight {
            padding: 1rem 1.1rem; margin-bottom: .75rem; border-radius: 18px;
            background: rgba(124,58,237,.12); border: 1px solid rgba(167,139,250,.18); color: #E2E8F0;
        }
        .ticker-card {
            padding: .95rem 1rem; border: 1px solid rgba(255,255,255,.10);
            background: rgba(15, 23, 42, .58); border-radius: 18px; text-align: center;
        }
        .ticker-symbol { color: #FFFFFF; font-size: 1.1rem; font-weight: 800; }
        .ticker-read { color: #94A3B8; font-size: .80rem; margin-top: .25rem; }
        div.stButton > button:first-child {
            width: 100%; border-radius: 18px; min-height: 3.3rem; border: 0;
            background: linear-gradient(135deg, #7C3AED, #2563EB);
            color: white; font-weight: 800; letter-spacing: .04em;
            box-shadow: 0 18px 45px rgba(37, 99, 235, .28);
        }
        div.stButton > button:first-child:hover { transform: translateY(-1px); filter: brightness(1.05); }
        .stTabs [data-baseweb="tab-list"] { gap: .4rem; }
        .stTabs [data-baseweb="tab"] {
            border-radius: 999px; padding: .55rem 1rem; background: rgba(255,255,255,.06);
            color: #CBD5E1;
        }
        .stTabs [aria-selected="true"] { background: rgba(124,58,237,.30); color: #FFFFFF; }
        </style>
        """,
        unsafe_allow_html=True,
    )
