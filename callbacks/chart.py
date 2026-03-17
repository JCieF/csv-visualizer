"""
callbacks/chart.py

Two callbacks:
  1. update_axis_dropdowns — repopulates X/Y dropdowns when new data is loaded
  2. render_chart          — re-renders the chart when type or axis selection changes
"""

from typing import Optional

import pandas as pd
from dash import Input, Output, State, callback
import plotly.graph_objects as go

from utils import ids
from utils.chart_builder import build_chart, CHART_PIE
from utils.type_detection import (
    COL_NUMERIC,
    COL_DATETIME,
    get_columns_by_type,
)

# Placeholder shown in the graph before axes are selected
EMPTY_FIGURE = go.Figure().update_layout(
    annotations=[{
        "text": "Select X and Y axes above to generate a chart.",
        "xref": "paper", "yref": "paper",
        "x": 0.5, "y": 0.5,
        "showarrow": False,
        "font": {"size": 16, "color": "#aaa"},
    }]
)


@callback(
    Output(ids.X_AXIS, "options"),
    Output(ids.X_AXIS, "value"),
    Output(ids.Y_AXIS, "options"),
    Output(ids.Y_AXIS, "value"),
    Input(ids.CSV_STORE, "data"),
)
def update_axis_dropdowns(
    store_data: Optional[dict],
) -> tuple[list, Optional[str], list, Optional[str]]:
    """
    Repopulate X and Y axis dropdowns whenever new CSV data is stored.

    - X axis: all columns (any type can be on X)
    - Y axis: numeric and datetime columns only (meaningful to plot as a value)
    Defaults to the first suitable column for each axis.
    """
    if store_data is None:
        return [], None, [], None

    all_columns: list[str] = store_data["columns"]
    col_types: dict[str, str] = store_data["col_types"]

    all_options = [{"label": col, "value": col} for col in all_columns]

    # Y axis should be numeric/datetime — meaningless to sum strings
    y_eligible = get_columns_by_type(col_types, COL_NUMERIC) + \
                 get_columns_by_type(col_types, COL_DATETIME)
    y_options = [{"label": col, "value": col} for col in y_eligible]

    # Pre-select sensible defaults: first column for X, first numeric for Y
    default_x = all_columns[0] if all_columns else None
    default_y = y_eligible[0] if y_eligible else None

    return all_options, default_x, y_options, default_y


@callback(
    Output(ids.CHART_GRAPH, "figure"),
    Input(ids.CHART_TYPE, "value"),
    Input(ids.X_AXIS, "value"),
    Input(ids.Y_AXIS, "value"),
    State(ids.CSV_STORE, "data"),
    prevent_initial_call=True,
)
def render_chart(
    chart_type: str,
    x_col: Optional[str],
    y_col: Optional[str],
    store_data: Optional[dict],
) -> go.Figure:
    """
    Re-render the chart whenever chart type or axis selection changes.

    For bar and pie charts, a Y column is optional (falls back to value counts).
    For line and scatter, Y is required — shows the empty placeholder if missing.
    """
    if store_data is None or x_col is None:
        return EMPTY_FIGURE

    # Pie chart works with just an X (label) column
    if chart_type != CHART_PIE and y_col is None:
        return EMPTY_FIGURE

    try:
        df = pd.DataFrame.from_records(store_data["records"])
        return build_chart(df, chart_type, x_col, y_col)
    except (ValueError, KeyError) as e:
        # Return empty figure with error annotation instead of crashing
        return go.Figure().update_layout(
            annotations=[{
                "text": f"Could not render chart: {e}",
                "xref": "paper", "yref": "paper",
                "x": 0.5, "y": 0.5,
                "showarrow": False,
                "font": {"size": 14, "color": "#e74c3c"},
            }]
        )
