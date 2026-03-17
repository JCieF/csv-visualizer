"""
utils/chart_builder.py

Builds Plotly figure objects from a DataFrame and a chart configuration.
All functions here are pure — no Dash imports, easy to unit-test.
"""

from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Supported chart types — keys are stored in dcc.Store / component values
CHART_BAR = "bar"
CHART_LINE = "line"
CHART_SCATTER = "scatter"
CHART_PIE = "pie"

CHART_TYPE_LABELS: dict[str, str] = {
    CHART_BAR: "Bar",
    CHART_LINE: "Line",
    CHART_SCATTER: "Scatter",
    CHART_PIE: "Pie",
}

# Plotly template used for all charts
CHART_TEMPLATE = "plotly_white"


def build_chart(
    df: pd.DataFrame,
    chart_type: str,
    x_col: str,
    y_col: Optional[str] = None,
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
        CHART_SCATTER: _build_scatter,
        CHART_PIE: _build_pie,
    }

    builder = builders.get(chart_type)
    if builder is None:
        raise ValueError(
            f"Unknown chart type '{chart_type}'. "
            f"Valid options: {list(builders.keys())}"
        )

    fig = builder(df, x_col, y_col)
    fig.update_layout(template=CHART_TEMPLATE)
    return fig


# ---------------------------------------------------------------------------
# Private builders — one per chart type
# ---------------------------------------------------------------------------

def _build_bar(df: pd.DataFrame, x_col: str, y_col: Optional[str]) -> go.Figure:
    if y_col is None:
        # No Y selected — show value counts of X
        counts = df[x_col].value_counts().reset_index()
        counts.columns = [x_col, "count"]
        return px.bar(counts, x=x_col, y="count", title=f"Count of {x_col}")
    return px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")


def _build_line(df: pd.DataFrame, x_col: str, y_col: Optional[str]) -> go.Figure:
    if y_col is None:
        raise ValueError("A Y-axis column is required for line charts.")
    return px.line(df, x=x_col, y=y_col, title=f"{y_col} over {x_col}")


def _build_scatter(df: pd.DataFrame, x_col: str, y_col: Optional[str]) -> go.Figure:
    if y_col is None:
        raise ValueError("A Y-axis column is required for scatter charts.")
    return px.scatter(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")


def _build_pie(df: pd.DataFrame, x_col: str, y_col: Optional[str]) -> go.Figure:
    """For pie charts, x_col = label column, y_col = value column (optional)."""
    if y_col:
        return px.pie(df, names=x_col, values=y_col, title=f"{y_col} by {x_col}")
    # No values column — use count of each category
    counts = df[x_col].value_counts().reset_index()
    counts.columns = [x_col, "count"]
    return px.pie(counts, names=x_col, values="count", title=f"Distribution of {x_col}")
