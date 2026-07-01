from __future__ import annotations

import streamlit as st


APP_CSS = """
<style>
:root {
  --msab-ink: #26313f;
  --msab-muted: #6f7a87;
  --msab-line: #d9e1ea;
  --msab-panel: #ffffff;
  --msab-soft: #f5f8fb;
  --msab-blue: #2f6f9f;
  --msab-teal: #2f756d;
  --msab-red: #c4514a;
}

.block-container {
  padding-top: 1.4rem;
  padding-bottom: 2rem;
  max-width: 1520px;
}

h1, h2, h3 {
  letter-spacing: 0;
  color: var(--msab-ink);
}

div[data-testid="stCaptionContainer"] {
  color: var(--msab-muted);
}

.msab-hero {
  border: 1px solid var(--msab-line);
  background: linear-gradient(180deg, #ffffff 0%, #f7fafc 100%);
  border-radius: 8px;
  padding: 18px 20px 16px 20px;
  margin-bottom: 16px;
}

.msab-hero-title {
  font-size: 30px;
  font-weight: 760;
  color: var(--msab-ink);
  margin: 0;
}

.msab-hero-subtitle {
  font-size: 13px;
  color: var(--msab-muted);
  margin-top: 6px;
  max-width: 820px;
}

.msab-status-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.msab-pill {
  border: 1px solid var(--msab-line);
  border-radius: 999px;
  background: #ffffff;
  color: var(--msab-ink);
  font-size: 12px;
  line-height: 1;
  padding: 8px 10px;
}

.msab-pill strong {
  color: var(--msab-blue);
  font-weight: 720;
}

.msab-panel-title {
  font-size: 17px;
  font-weight: 720;
  color: var(--msab-ink);
  margin: 0 0 3px 0;
}

.msab-panel-subtitle {
  font-size: 12px;
  color: var(--msab-muted);
  margin: 0 0 14px 0;
}

.msab-muted {
  color: var(--msab-muted);
}

.msab-empty {
  border: 1px dashed #cbd7e3;
  background: #f8fbfd;
  border-radius: 8px;
  padding: 22px;
}

.msab-empty h2 {
  font-size: 22px;
  margin: 0 0 6px 0;
}

.msab-empty p {
  margin: 0;
  color: var(--msab-muted);
  font-size: 13px;
}

div[data-testid="stMetric"] {
  border: 1px solid var(--msab-line);
  border-radius: 8px;
  background: var(--msab-panel);
  padding: 12px 12px 10px 12px;
}

div[data-testid="stMetricLabel"] {
  color: var(--msab-muted);
}

div[data-testid="stMetricValue"] {
  color: var(--msab-ink);
  font-size: 24px;
}

.msab-metric-card {
  border: 1px solid var(--msab-line);
  border-radius: 8px;
  background: #ffffff;
  padding: 12px;
  min-height: 84px;
}

.msab-metric-label {
  color: var(--msab-muted);
  font-size: 12px;
  line-height: 1.25;
  overflow-wrap: anywhere;
}

.msab-metric-value {
  color: var(--msab-ink);
  font-size: 24px;
  line-height: 1.2;
  margin-top: 8px;
  font-variant-numeric: tabular-nums;
  overflow-wrap: anywhere;
}

div[data-testid="stDataFrame"] {
  border: 1px solid var(--msab-line);
  border-radius: 8px;
}

.stButton > button,
div[data-testid="stDownloadButton"] button {
  border-radius: 8px;
  min-height: 40px;
  font-weight: 650;
}

button[data-testid="stBaseButton-primary"] {
  background: var(--msab-blue);
  border-color: var(--msab-blue);
}

button[data-testid="stBaseButton-primary"]:hover {
  background: #265b83;
  border-color: #265b83;
}

button[data-testid="stBaseButton-segmented_controlActive"] {
  background: #e9f3f5;
  border-color: var(--msab-teal);
  color: var(--msab-teal);
}

button[data-testid="stBaseButton-segmented_controlActive"] p {
  color: var(--msab-teal);
}

div[data-testid="stSegmentedControl"] button {
  border-radius: 8px;
}

div[data-testid="stAlert"] {
  border-radius: 8px;
}
</style>
"""


def apply_app_style() -> None:
    st.markdown(APP_CSS, unsafe_allow_html=True)
