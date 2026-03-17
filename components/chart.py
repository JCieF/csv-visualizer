"""
components/chart.py

Chart display panel: chart type selector, X/Y axis dropdowns,
smart-pie suggestion banner, and the graph itself.

The panel is hidden on initial load and revealed by a callback once data
is uploaded.
"""

import dash_bootstrap_components as dbc
from dash import dcc, html

from utils import ids
from utils.chart_builder import CHART_TYPE_LABELS

# Build dropdown options from the chart type constants — no hardcoded strings
CHART_TYPE_OPTIONS = [
    {"label": label, "value": value}
    for value, label in CHART_TYPE_LABELS.items()
]

# Default chart type shown on first render after upload
DEFAULT_CHART_TYPE = "bar"

# Inline styles toggled by the upload callback
HIDDEN_STYLE = {"display": "none"}
VISIBLE_STYLE = {"display": "block"}


def create_chart_panel() -> html.Div:
    """
    Build and return the chart configuration + display panel.

    Contains:
        - Chart type selector (radio buttons)
        - X-axis column dropdown
        - Y-axis column dropdown
        - Smart-pie suggestion banner (hidden until needed)
        - dcc.Graph for the rendered Plotly figure

    Initially hidden; the upload callback sets style to VISIBLE_STYLE.
    """
    return html.Div(
        id=ids.CHART_PANEL,
        style=HIDDEN_STYLE,
        children=[
            dbc.Card(
                dbc.CardBody([

                    # ── Section header ────────────────────────────────────
                    html.Div([
                        html.I(className="bi bi-sliders me-2"),
                        html.Span("Chart Configuration"),
                    ], className="section-header mb-3"),

                    # ── Controls row: type selector + axis dropdowns ──────
                    dbc.Row([

                        # Chart type
                        dbc.Col([
                            dbc.Label(
                                [html.I(className="bi bi-pie-chart me-1"), " Chart Type"],
                                html_for=ids.CHART_TYPE,
                                className="form-label-styled",
                            ),
                            dbc.RadioItems(
                                id=ids.CHART_TYPE,
                                options=CHART_TYPE_OPTIONS,
                                value=DEFAULT_CHART_TYPE,
                                inline=True,
                                className="chart-type-radio",
                            ),
                        ], width=12, lg=4, className="mb-3 mb-lg-0"),

                        # X axis
                        dbc.Col([
                            dbc.Label(
                                [html.I(className="bi bi-arrow-right me-1"), " X Axis"],
                                html_for=ids.X_AXIS,
                                className="form-label-styled",
                            ),
                            dcc.Dropdown(
                                id=ids.X_AXIS,
                                placeholder="Select a column…",
                                clearable=False,
                                className="axis-dropdown",
                            ),
                        ], width=12, sm=6, lg=4, className="mb-3 mb-lg-0"),

                        # Y axis
                        dbc.Col([
                            dbc.Label(
                                [html.I(className="bi bi-arrow-up me-1"), " Y Axis"],
                                html_for=ids.Y_AXIS,
                                className="form-label-styled",
                            ),
                            dcc.Dropdown(
                                id=ids.Y_AXIS,
                                placeholder="Optional for Bar / Pie",
                                clearable=True,
                                className="axis-dropdown",
                            ),
                        ], width=12, sm=6, lg=4),

                    ], className="mb-4"),

                    # ── Smart-pie suggestion banner ───────────────────────
                    # Hidden by default; the update_suggestion callback
                    # opens it when a pie chart has too many categories.
                    # suppress_callback_exceptions=True in app.py allows the
                    # CHART_SUGGESTION_BTN id to be rendered dynamically
                    # inside the alert children without raising layout errors.
                    dbc.Alert(
                        id=ids.CHART_SUGGESTION,
                        is_open=False,
                        dismissable=True,
                        color="warning",
                        className="suggestion-alert mb-3",
                    ),

                    # ── Chart graph ───────────────────────────────────────
                    dcc.Graph(
                        id=ids.CHART_GRAPH,
                        config={
                            # Show the Plotly toolbar; enable crisp PNG export
                            "displayModeBar": True,
                            "toImageButtonOptions": {
                                "format": "png",
                                "filename": "chart",
                                "scale": 2,
                            },
                        },
                        className="chart-graph",
                    ),

                ]),
                className="chart-card mb-4",
            )
        ],
    )
