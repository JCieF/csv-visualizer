"""
CSV Data Visualizer — Main Application Entry Point

Initializes the Dash app, sets the layout, and registers all callbacks.
Run with: python app.py
"""

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,  # needed once dynamic components are added
    title="CSV Data Visualizer",
)

# Expose the Flask server for deployment (e.g., Gunicorn)
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
        # Theme toggle store — tracks light/dark mode state
        dcc.Store(id="theme-store", data={"dark": False}),

        navbar,

        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        html.H4("Welcome!", className="text-center mt-5"),
                        html.P(
                            "Upload a CSV file to get started.",
                            className="text-center text-muted",
                        ),
                    ]
                )
            )
        ),
    ],
    fluid=True,
    id="main-container",
)

# ---------------------------------------------------------------------------
# Register callbacks (imported here to avoid circular imports)
# ---------------------------------------------------------------------------
# from callbacks import upload, chart, filter  # uncomment as callbacks are built

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
