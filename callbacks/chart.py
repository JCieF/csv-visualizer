"""
callbacks/chart.py

Five callbacks:
  1. update_axis_dropdowns — repopulates X/Y dropdowns when new CSV data is loaded
  2. auto_select_chart_type — picks the most logical chart type when columns change
  3. render_chart           — re-renders the chart when type or axis selection changes
  4. update_suggestion      — shows/hides the smart-pie / aggregation banners
  5. switch_to_bar          — switches chart type to horizontal bar when banner button clicked
"""

from typing import Optional

import pandas as pd
from dash import Input, Output, State, callback, html, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from utils import ids
from utils.chart_builder import (
    build_chart,
    CHART_BAR, CHART_LINE, CHART_AREA, CHART_SCATTER, CHART_PIE, CHART_BAR_H,
    CHART_TEMPLATE_LIGHT, CHART_TEMPLATE_DARK,
)
from utils.smart_pie import get_pie_status
from utils.type_detection import (
    COL_NUMERIC,
    COL_DATETIME,
    COL_CATEGORICAL,
    get_columns_by_type,
)


def _best_chart_type(
    x_col: str,
    y_col: Optional[str],
    col_types: dict[str, str],
    n_unique_x: int,
) -> str:
    """
    Return the most readable chart type for the given column combination.

    Rules (in priority order):
      • No Y selected
          - numeric X   → Bar (distribution / histogram)
          - categorical X, ≤ 8 unique values → Pie
          - categorical X, > 8 unique values → Horizontal Bar (labels fit better)
      • Y selected
          - categorical X + numeric Y → Bar (mean per group)
          - datetime X   + numeric Y → Area (trend over time)
          - numeric X    + numeric Y → Scatter (relationship)
    """
    x_type = col_types.get(x_col, COL_CATEGORICAL)
    y_type = col_types.get(y_col, COL_NUMERIC) if y_col else None

    if y_col is None or y_col == x_col:
        if x_type == COL_NUMERIC:
            return CHART_BAR
        if n_unique_x <= 8:
            return CHART_PIE
        return CHART_BAR_H

    if x_type == COL_CATEGORICAL:
        return CHART_BAR_H if n_unique_x > 8 else CHART_BAR
    if x_type == COL_DATETIME:
        return CHART_AREA
    # Both numeric
    return CHART_SCATTER

# Placeholder shown in the graph before axes are selected
_PLACEHOLDER_ANNOTATION = {
    "xref": "paper",
    "yref": "paper",
    "x": 0.5,
    "y": 0.5,
    "showarrow": False,
}

EMPTY_FIGURE = go.Figure().update_layout(
    annotations=[{
        **_PLACEHOLDER_ANNOTATION,
        "text": "Select X and Y axes above to generate a chart.",
        "font": {"size": 16, "color": "#94a3b8"},
    }],
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)


# ---------------------------------------------------------------------------
# 1. Repopulate axis dropdowns when data changes
# ---------------------------------------------------------------------------

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

    - X axis: all columns (any type can be placed on X)
    - Y axis: numeric and datetime columns only (meaningful to plot as a value)

    Pre-selects the first suitable column for each axis as a sensible default.
    """
    if store_data is None:
        return [], None, [], None

    all_columns: list[str] = store_data["columns"]
    col_types: dict[str, str] = store_data["col_types"]

    all_options = [{"label": col, "value": col} for col in all_columns]

    # Y axis should be numeric or datetime — summing/averaging strings is meaningless
    y_eligible = (
        get_columns_by_type(col_types, COL_NUMERIC)
        + get_columns_by_type(col_types, COL_DATETIME)
    )
    y_options = [{"label": col, "value": col} for col in y_eligible]

    default_x = all_columns[0] if all_columns else None
    default_y = y_eligible[0] if y_eligible else None

    return all_options, default_x, y_options, default_y


# ---------------------------------------------------------------------------
# 2. Auto-select chart type when columns change
# ---------------------------------------------------------------------------

@callback(
    Output(ids.CHART_TYPE, "value", allow_duplicate=True),
    Input(ids.X_AXIS, "value"),
    Input(ids.Y_AXIS, "value"),
    State(ids.CSV_STORE, "data"),
    prevent_initial_call=True,
)
def auto_select_chart_type(
    x_col: Optional[str],
    y_col: Optional[str],
    store_data: Optional[dict],
) -> str:
    """
    When the user changes X or Y, automatically switch to the most
    readable chart type for that column combination.
    The user can still override manually afterward.
    """
    if store_data is None or x_col is None:
        return no_update

    col_types: dict[str, str] = store_data.get("col_types", {})
    try:
        df = pd.DataFrame.from_records(store_data["records"])
        n_unique_x = df[x_col].nunique()
    except (KeyError, Exception):
        return no_update

    return _best_chart_type(x_col, y_col, col_types, n_unique_x)


# ---------------------------------------------------------------------------
# 3. Render the chart
# ---------------------------------------------------------------------------

@callback(
    Output(ids.CHART_GRAPH, "figure"),
    Input(ids.CHART_TYPE, "value"),
    Input(ids.X_AXIS, "value"),
    Input(ids.Y_AXIS, "value"),
    Input(ids.THEME_STORE, "data"),
    State(ids.CSV_STORE, "data"),
    prevent_initial_call=True,
)
def render_chart(
    chart_type: str,
    x_col: Optional[str],
    y_col: Optional[str],
    theme_data: Optional[dict],
    store_data: Optional[dict],
) -> go.Figure:
    """
    Re-render the chart whenever the chart type or axis selection changes.

    For bar and pie charts, a Y column is optional (falls back to value counts).
    For line and scatter, Y is required — returns an empty placeholder if missing.
    """
    if store_data is None or x_col is None:
        return EMPTY_FIGURE

    # Pie and bar charts work with just an X (label/category) column
    requires_y = chart_type not in (CHART_PIE, "bar", "bar_h")
    if requires_y and (y_col is None or y_col == x_col):
        return EMPTY_FIGURE

    dark_mode = (theme_data or {}).get("dark", False)

    try:
        df = pd.DataFrame.from_records(store_data["records"])
        return build_chart(df, chart_type, x_col, y_col, dark_mode=dark_mode)
    except (ValueError, KeyError) as exc:
        return go.Figure().update_layout(
            annotations=[{
                **_PLACEHOLDER_ANNOTATION,
                "text": f"Could not render chart: {exc}",
                "font": {"size": 14, "color": "#ef4444"},
            }]
        )


# ---------------------------------------------------------------------------
# 4. Smart-pie / aggregation suggestion banner
# ---------------------------------------------------------------------------

@callback(
    Output(ids.CHART_SUGGESTION, "is_open"),
    Output(ids.CHART_SUGGESTION, "children"),
    Output(ids.CHART_SUGGESTION, "color"),
    Input(ids.CHART_TYPE, "value"),
    Input(ids.X_AXIS, "value"),
    Input(ids.Y_AXIS, "value"),
    State(ids.CSV_STORE, "data"),
)
def update_suggestion(
    chart_type: Optional[str],
    x_col: Optional[str],
    y_col: Optional[str],
    store_data: Optional[dict],
) -> tuple[bool, list, str]:
    """
    Show contextual banners:
    - Pie with too many categories → suggest horizontal bar
    - Pie truncated → info about top-N display
    - Line chart with duplicate X values → inform that data is averaged (mean)
    """
    if store_data is None or x_col is None:
        return False, [], "info"

    try:
        df = pd.DataFrame.from_records(store_data["records"])

        # ── Pie suggestions ───────────────────────────────────────────────
        if chart_type == CHART_PIE:
            status, message = get_pie_status(df, x_col, chart_type)

            if status == "suggest_bar":
                children = [
                    html.I(className="bi bi-exclamation-triangle-fill me-2"),
                    html.Span(message),
                    dbc.Button(
                        [
                            html.I(className="bi bi-bar-chart-line me-1"),
                            "Switch to Horizontal Bar",
                        ],
                        id=ids.CHART_SUGGESTION_BTN,
                        size="sm",
                        color="warning",
                        outline=True,
                        className="ms-3 suggestion-btn",
                    ),
                ]
                return True, children, "warning"

            if status == "truncated":
                children = [
                    html.I(className="bi bi-info-circle-fill me-2"),
                    html.Span(message),
                ]
                return True, children, "info"

        # ── Line / Area with duplicate X values ───────────────────────────
        if chart_type in ("line", CHART_AREA) and y_col and y_col != x_col:
            if df[x_col].duplicated().any():
                unique = df[x_col].nunique()
                total = len(df)
                children = [
                    html.I(className="bi bi-info-circle-fill me-2"),
                    html.Span(
                        f"X axis has {total:,} rows but only {unique:,} unique values — "
                        f"chart shows the mean {y_col} per {x_col} value."
                    ),
                ]
                return True, children, "info"

    except (KeyError, ValueError):
        pass

    return False, [], "info"


# ---------------------------------------------------------------------------
# 5. Switch to horizontal bar when the banner button is clicked
# ---------------------------------------------------------------------------

@callback(
    Output(ids.CHART_TYPE, "value"),
    Input(ids.CHART_SUGGESTION_BTN, "n_clicks"),
    prevent_initial_call=True,
)
def switch_to_horizontal_bar(_n_clicks: Optional[int]) -> str:
    """
    Flip the chart type radio to 'Horizontal Bar' when the user clicks
    the suggestion banner button. The chart and banner update reactively
    via the render_chart and update_suggestion callbacks.
    """
    return CHART_BAR_H
