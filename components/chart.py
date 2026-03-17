"""
components/chart.py

Chart display panel: chart type selector, X/Y axis dropdowns, and the graph.
The panel is hidden on initial load and revealed by a callback once data is uploaded.
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

# Inline style applied to the panel before data is loaded
HIDDEN_STYLE = {"display": "none"}
VISIBLE_STYLE = {"display": "block"}


def create_chart_panel() -> html.Div:
    """
    Build and return the chart configuration + display panel.

    Contains:
        - Chart type selector (radio buttons)
        - X-axis column dropdown
        - Y-axis column dropdown
        - dcc.Graph for the rendered Plotly figure

    Initially hidden; the upload callback sets style to VISIBLE_STYLE.
    """
    return html.Div(
        id=ids.CHART_PANEL,
        style=HIDDEN_STYLE,
        children=[
            dbc.Card(
                dbc.CardBody([
                    html.H5("Chart Configuration", className="card-title mb-3"),

                    dbc.Row([
                        # Chart type selector
                        dbc.Col([
                            dbc.Label("Chart Type", html_for=ids.CHART_TYPE),
                            dbc.RadioItems(
                                id=ids.CHART_TYPE,
                                options=CHART_TYPE_OPTIONS,
                                value=DEFAULT_CHART_TYPE,
                                inline=True,
                                className="mb-0",
                            ),
                        ], width=12, lg=4, className="mb-3 mb-lg-0"),

                        # X axis
                        dbc.Col([
                            dbc.Label("X Axis", html_for=ids.X_AXIS),
                            dcc.Dropdown(
                                id=ids.X_AXIS,
                                placeholder="Select a column…",
                                clearable=False,
                            ),
                        ], width=12, sm=6, lg=4, className="mb-3 mb-lg-0"),

                        # Y axis
                        dbc.Col([
                            dbc.Label("Y Axis", html_for=ids.Y_AXIS),
                            dcc.Dropdown(
                                id=ids.Y_AXIS,
                                placeholder="Select a column… (optional for bar/pie)",
                                clearable=True,
                            ),
                        ], width=12, sm=6, lg=4),
                    ], className="mb-4"),

                    dcc.Graph(
                        id=ids.CHART_GRAPH,
                        config={
                            # Enable the Plotly toolbar for zoom, pan, and PNG export
                            "displayModeBar": True,
                            "toImageButtonOptions": {
                                "format": "png",
                                "filename": "chart",
                                "scale": 2,  # 2x resolution for crisp exports
                            },
                        },
                    ),
                ]),
                className="mb-4",
            )
        ],
    )
