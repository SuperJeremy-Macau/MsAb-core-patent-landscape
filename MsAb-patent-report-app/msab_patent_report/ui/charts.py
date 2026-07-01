from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def yearly_trend_chart(rows: list[dict], title: str) -> go.Figure:
    if not rows:
        fig = go.Figure()
        fig.update_layout(title=title, xaxis_title="Year", yaxis_title="Patent publications", template="plotly_white")
        return fig
    df = pd.DataFrame(rows).sort_values("year")
    fig = px.line(df, x="year", y="patent_count", markers=True, title=title, template="plotly_white")
    fig.update_traces(line_color="#2f6f9f", marker=dict(size=7, color="#c4514a"))
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Patent publications",
        margin=dict(l=10, r=10, t=45, b=10),
        hovermode="x unified",
    )
    return fig


def bar_chart(rows: list[dict], x: str, y: str, title: str) -> go.Figure:
    if not rows:
        fig = go.Figure()
        fig.update_layout(title=title, xaxis_title=x, yaxis_title=y, template="plotly_white")
        return fig
    df = pd.DataFrame(rows)
    fig = px.bar(df, x=x, y=y, title=title, template="plotly_white")
    fig.update_traces(marker_color="#2f756d")
    fig.update_layout(
        xaxis_title=x.replace("_", " ").title(),
        yaxis_title=y.replace("_", " ").title(),
        margin=dict(l=10, r=10, t=45, b=10),
    )
    return fig
