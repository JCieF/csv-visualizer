"""
CSV Data Visualizer — Main Application Entry Point

Initializes the Dash app, assembles the layout from components,
then imports callbacks to register them with the app.

Run locally:  python app.py
Production:   gunicorn app:server
"""

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from components.upload import create_upload_component
from components.chart import create_chart_panel
from utils import ids

# ---------------------------------------------------------------------------
# App initialisation
# ---------------------------------------------------------------------------

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        # Bootstrap Icons — used for the upload cloud icon
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css",
    ],
    suppress_callback_exceptions=True,
    title="CSV Data Visualizer",
)

# Expose the Flask server for Gunicorn / Vercel deployment
server = app.server

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

navbar = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand("CSV Data Visualizer", className="fw-bold"),
    ]),
    color="primary",
    dark=True,
    className="mb-4",
)

app.layout = dbc.Container(
    [
        # Stores — persist state across callbacks without re-parsing
        dcc.Store(id=ids.CSV_STORE),
        dcc.Store(id=ids.THEME_STORE, data={"dark": False}),

        navbar,

        dbc.Row(
            dbc.Col(
                [
                    create_upload_component(),
                    create_chart_panel(),
                ],
                width=12,
                xl=10,
                className="mx-auto",
            )
        ),
    ],
    fluid=True,
    id=ids.MAIN_CONTAINER,
)

# ---------------------------------------------------------------------------
# Register callbacks
# Imported AFTER layout is defined to avoid circular import issues.
# The `noqa` comments suppress linting warnings for "imported but unused".
# ---------------------------------------------------------------------------

import callbacks.upload  # noqa: E402, F401
import callbacks.chart   # noqa: E402, F401

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
