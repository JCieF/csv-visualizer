"""
components/navbar.py

Top navigation bar with brand identity and dark / light mode toggle.
The toggle button cycles between moon (switch to dark) and sun (switch to light).
The actual theme switch is handled by callbacks/theme.py.
"""

import dash_bootstrap_components as dbc
from dash import html

from utils import ids


def create_navbar() -> dbc.Navbar:
    """Build and return the application navbar."""
    return dbc.Navbar(
        dbc.Container(
            [
                # Brand — icon + title
                dbc.NavbarBrand(
                    [
                        html.I(className="bi bi-bar-chart-fill me-2"),
                        "CSV Data Visualizer",
                    ],
                    className="app-brand",
                ),

                # Dark / light mode toggle — pushes to the right via ms-auto
                dbc.Button(
                    html.I(
                        id=ids.THEME_TOGGLE_ICON,
                        className="bi bi-moon-fill",  # default: show moon (light mode)
                    ),
                    id=ids.DARK_MODE_TOGGLE,
                    color="link",
                    className="theme-toggle-btn ms-auto",
                    n_clicks=0,
                    title="Toggle dark mode",
                ),
            ],
            fluid=True,
            className="d-flex align-items-center",
        ),
        className="app-navbar mb-4",
    )
