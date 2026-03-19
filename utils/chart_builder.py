"""
utils/chart_builder.py

Builds Plotly figure objects from a DataFrame and a chart configuration.
All functions here are pure — no Dash imports, easy to unit-test.
"""

from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.smart_pie import prepare_pie_data, PIE_TOP_N, CARDINALITY_PIE_MAX

# Supported chart types — keys are stored in dcc.Store / component values
CHART_BAR = "bar"
CHART_LINE = "line"
CHART_SCATTER = "scatter"
CHART_PIE = "pie"
CHART_BAR_H = "bar_h"  # horizontal bar — best for high-cardinality categorical data

CHART_AREA = "area"

CHART_TYPE_LABELS: dict[str, str] = {
    CHART_BAR: "Bar",
    CHART_LINE: "Line",
    CHART_AREA: "Area",
    CHART_SCATTER: "Scatter",
    CHART_PIE: "Pie",
    CHART_BAR_H: "Horizontal Bar",
}

# Plotly templates — light uses clean white grid, dark matches the navy UI
CHART_TEMPLATE_LIGHT = "plotly_white"
CHART_TEMPLATE_DARK  = "plotly_dark"

# Shared font applied to all charts (matches the UI Inter font)
_CHART_FONT = dict(family="Inter, system-ui, -apple-system, sans-serif")

# Color scale used for bar charts — maps bar height to a gradient
_BAR_COLORSCALE = "Teal"


def build_chart(
    df: pd.DataFrame,
    chart_type: str,
    x_col: str,
    y_col: Optional[str] = None,
    dark_mode: bool = False,
) -> go.Figure:
    """
    Build and return a Plotly figure for the given chart type and columns.

    Args:
        df:         Source DataFrame (already filtered if applicable).
        chart_type: One of CHART_BAR, CHART_LINE, CHART_SCATTER, CHART_PIE.
        x_col:      Column to use for the X axis (or pie labels).
        y_col:      Column to use for the Y axis (or pie values).
                    Required for all chart types except single-value pies.

    Returns:
        A Plotly Figure object ready to pass to dcc.Graph.

    Raises:
        ValueError: If chart_type is not recognised or required columns are missing.
    """
    if x_col not in df.columns:
        raise ValueError(f"Column '{x_col}' not found in the dataset.")
    if y_col is not None and y_col not in df.columns:
        raise ValueError(f"Column '{y_col}' not found in the dataset.")

    builders = {
        CHART_BAR: _build_bar,
        CHART_LINE: _build_line,
        CHART_AREA: _build_area,
        CHART_SCATTER: _build_scatter,
        CHART_PIE: _build_pie,
        CHART_BAR_H: _build_bar_horizontal,
    }

    builder = builders.get(chart_type)
    if builder is None:
        raise ValueError(
            f"Unknown chart type '{chart_type}'. "
            f"Valid options: {list(builders.keys())}"
        )

    fig = builder(df, x_col, y_col)
    fig.update_layout(
        template=CHART_TEMPLATE_DARK if dark_mode else CHART_TEMPLATE_LIGHT,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)" if dark_mode else "#ffffff",
        font=_CHART_FONT,
    )
    return fig


# ---------------------------------------------------------------------------
# Private builders — one per chart type
# ---------------------------------------------------------------------------

def _build_bar_horizontal(df: pd.DataFrame, x_col: str, y_col: Optional[str]) -> go.Figure:
    """
    Horizontal bar chart — ideal for high-cardinality categorical columns
    where vertical labels would overlap. Categories go on the Y axis.
    """
    if y_col is None:
        counts = df[x_col].value_counts().reset_index()
        counts.columns = [x_col, "count"]
        # Sort ascending so the largest bar is at the top of the chart
        counts = counts.sort_values("count", ascending=True)
        return px.bar(counts, x="count", y=x_col, orientation="h", title=f"Count of {x_col}")
    sorted_df = df.sort_values(y_col, ascending=True)
    return px.bar(sorted_df, x=y_col, y=x_col, orientation="h", title=f"{y_col} by {x_col}")


def _build_bar(df: pd.DataFrame, x_col: str, y_col: Optional[str]) -> go.Figure:
    # When no Y is selected, or the user picks the same column for both axes,
    # show a frequency count — summing a column against itself produces
    # misleading totals (e.g. 400 students × 20 hrs = 8 000 on the Y axis).
    if y_col is None or y_col == x_col:
        counts = df[x_col].value_counts().reset_index()
        counts.columns = [x_col, "count"]
        counts = counts.sort_values(x_col)
        fig = px.bar(
            counts, x=x_col, y="count",
            title=f"Distribution of {x_col}",
            color="count",
            color_continuous_scale=_BAR_COLORSCALE,
        )
        fig.update_layout(coloraxis_showscale=False)
        return fig

    # When X has duplicate values (e.g. categorical like Teacher_Quality),
    # summing Y produces meaningless totals (80k = sum of all Hours_Studied
    # for that category). Aggregate to mean so bars show the average Y per group.
    if df[x_col].duplicated().any():
        agg = df.groupby(x_col, sort=False)[y_col].mean().reset_index()
        agg = agg.sort_values(y_col, ascending=False)
        fig = px.bar(
            agg, x=x_col, y=y_col,
            title=f"Mean {y_col} by {x_col}",
            color=y_col,
            color_continuous_scale=_BAR_COLORSCALE,
        )
        fig.update_layout(coloraxis_showscale=False)
        return fig

    fig = px.bar(
        df, x=x_col, y=y_col,
        title=f"{y_col} by {x_col}",
        color=y_col,
        color_continuous_scale=_BAR_COLORSCALE,
    )
    fig.update_layout(coloraxis_showscale=False)
    return fig


def _aggregate_for_line(df: pd.DataFrame, x_col: str, y_col: str) -> tuple[pd.DataFrame, bool]:
    """
    If the X column has duplicate values (e.g. integer attendance 60-100 with
    thousands of students), plotting raw rows creates a spider-web mess.
    Aggregate to mean Y per unique X and signal that aggregation was applied.
    """
    has_duplicates = df[x_col].duplicated().any()
    if has_duplicates:
        agg = df.groupby(x_col, sort=True)[y_col].mean().reset_index()
        return agg, True
    return df.sort_values(x_col), False


def _build_line(df: pd.DataFrame, x_col: str, y_col: Optional[str]) -> go.Figure:
    if y_col is None:
        raise ValueError("A Y-axis column is required for line charts.")
    agg_df, was_aggregated = _aggregate_for_line(df, x_col, y_col)
    title = f"{y_col} over {x_col}"
    if was_aggregated:
        title += " (mean per value)"
    return px.line(agg_df, x=x_col, y=y_col, title=title)


def _build_area(df: pd.DataFrame, x_col: str, y_col: Optional[str]) -> go.Figure:
    """
    Filled area chart with spline smoothing — good for showing trends over a
    continuous or ordered X axis. Aggregates duplicate X values same as line.
    """
    if y_col is None:
        raise ValueError("A Y-axis column is required for area charts.")
    agg_df, was_aggregated = _aggregate_for_line(df, x_col, y_col)
    title = f"{y_col} over {x_col}"
    if was_aggregated:
        title += " (mean per value)"
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=agg_df[x_col],
        y=agg_df[y_col],
        mode="lines",
        fill="tozeroy",
        line=dict(shape="spline", smoothing=1.3, color="#2dd4bf", width=2),
        fillcolor="rgba(45, 212, 191, 0.25)",
        name=y_col,
    ))
    fig.update_layout(title=title, xaxis_title=x_col, yaxis_title=y_col)
    return fig


def _build_scatter(df: pd.DataFrame, x_col: str, y_col: Optional[str]) -> go.Figure:
    if y_col is None:
        raise ValueError("A Y-axis column is required for scatter charts.")
    return px.scatter(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")


def _build_pie(df: pd.DataFrame, x_col: str, y_col: Optional[str]) -> go.Figure:
    """
    For pie charts, x_col = label column, y_col = value column (optional).

    If the column has more than PIE_TOP_N unique values, data is automatically
    truncated to the top N categories with the rest grouped as "Other".
    For columns exceeding CARDINALITY_PIE_MAX, the caller (callback) should
    have already suggested switching to a bar chart; we still render the pie
    with top-N grouping as a fallback.
    """
    # Prepare data — limits to top PIE_TOP_N and groups the rest as "Other"
    prepared = prepare_pie_data(df, x_col, y_col, top_n=PIE_TOP_N)

    value_col = y_col if y_col else "count"
    title = f"{y_col} by {x_col}" if y_col else f"Distribution of {x_col}"

    unique_count = df[x_col].nunique()
    if unique_count > PIE_TOP_N:
        title += f" (top {PIE_TOP_N} of {unique_count:,})"

    return px.pie(prepared, names=x_col, values=value_col, title=title)
