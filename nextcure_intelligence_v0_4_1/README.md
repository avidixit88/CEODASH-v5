# NextCure Intelligence System v0.4

CEO-facing Streamlit prototype for the Week 1 Market Positioning Layer.

## What v0.4 adds

- Classification engine for NXTC vs XBI / QQQ
- Explicit 1D, 5D, 30D, 60D, and 90D return windows
- Channel engine for:
  - CDH6 / Ovarian ADC
  - B7-H4 ADC
  - Ovarian Cancer
  - ADC Capital Flow
  - Small-Cap Oncology
  - Alzheimer's Side Channel
  - Bone Disease Side Channel
- Insight engine that converts real market data into CEO-readable observations
- Channel Intelligence tab with 30D average bars and 5D momentum markers
- Return-table expander for auditability without cluttering the main UI

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## CTO notes

The dashboard remains one-button and backend-driven. Operational choices such as peer lists, channels, thresholds, and lookback windows live in config/ and engines/, not in exposed Streamlit controls.


## v0.4.1 adjustment

Promoted the 90D return window into a CEO-facing Quarterly View. The math was already present in v0.4, but v0.4.1 adds quarterly classification, quarterly watch-card language, and quarterly context in executive insights/channel readouts.
