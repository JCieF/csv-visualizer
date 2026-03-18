"""
callbacks/theme.py

Toggles dark mode by adding / removing the .dark-mode class on #main-container.
Also flips the navbar icon between moon (light) and sun (dark).
"""

from typing import Optional

from dash import Input, Output, State, callback

from utils import ids

_LIGHT_ICON = "bi bi-moon-fill"
_DARK_ICON  = "bi bi-sun-fill"


@callback(
    Output(ids.MAIN_CONTAINER, "className"),
    Output(ids.THEME_STORE, "data"),
    Output(ids.THEME_TOGGLE_ICON, "className"),
    Input(ids.DARK_MODE_TOGGLE, "n_clicks"),
    State(ids.THEME_STORE, "data"),
    prevent_initial_call=True,
)
def toggle_theme(
    n_clicks: Optional[int],
    store_data: Optional[dict],
) -> tuple[str, dict, str]:
    """
    Each click flips the current theme.

    Returns:
        - className for #main-container ("dark-mode" or "")
        - updated theme store dict
        - className for the toggle icon (sun or moon)
    """
    is_dark = not (store_data or {}).get("dark", False)
    return (
        "dark-mode" if is_dark else "",
        {"dark": is_dark},
        _DARK_ICON if is_dark else _LIGHT_ICON,
    )
