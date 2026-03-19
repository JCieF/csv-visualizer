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
from dotenv import load_dotenv

load_dotenv()

from components.navbar import create_navbar
from components.hero import create_welcome_hero
from components.upload import create_upload_component
from components.chart import create_chart_panel
from components.column_summary import create_column_summary_section
from components.insights_panel import create_insights_panel
from utils import ids

# ---------------------------------------------------------------------------
# App initialisation
# ---------------------------------------------------------------------------

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        # Bootstrap Icons
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css",
        # Inter — professional sans-serif used throughout the UI
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
    suppress_callback_exceptions=True,
    title="CSV Data Visualizer",
)

# Expose the Flask server for Gunicorn / Vercel deployment
server = app.server

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

app.layout = dbc.Container(
    [
        # Stores — persist state across callbacks without re-parsing
        dcc.Store(id=ids.CSV_STORE),
        dcc.Store(id=ids.THEME_STORE, data={"dark": False}),
        dcc.Store(id=ids.INSIGHTS_RULE_STORE),

        create_navbar(),

        dbc.Row(
            dbc.Col(
                [
                    # Wrapper div drives the viewport-center → layout-position transition.
                    # On load: padding-top pushes the card to the vertical center.
                    # After upload: the callback sets className="upload-anchored",
                    # collapsing the padding and sliding the card to its final spot.
                    html.Div(
                        [
                            create_welcome_hero(),
                            create_upload_component(),
                        ],
                        id=ids.UPLOAD_WRAPPER,
                        className="upload-wrapper",
                    ),
                    dbc.Container(id="section-divider-1", class_name="section-divider-wrap"),
                    create_insights_panel(),
                    dbc.Container(id="section-divider-2", class_name="section-divider-wrap"),
                    create_column_summary_section(),
                    dbc.Container(id="section-divider-3", class_name="section-divider-wrap"),
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
    className="",
)

# ---------------------------------------------------------------------------
# Register callbacks
# Imported AFTER layout is defined to avoid circular import issues.
# The `noqa` comments suppress linting warnings for "imported but unused".
# ---------------------------------------------------------------------------

import callbacks.upload          # noqa: E402, F401
import callbacks.chart            # noqa: E402, F401
import callbacks.column_summary   # noqa: E402, F401
import callbacks.theme            # noqa: E402, F401
import callbacks.insights         # noqa: E402, F401

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
