"""
callbacks/upload.py

Handles the CSV file upload event:
  1. Parses the file via utils.csv_parser
  2. Detects column types via utils.type_detection
  3. Serialises the DataFrame + metadata to JSON and stores it in dcc.Store
  4. Shows compact inline success/error feedback below the dropzone
  5. Reveals the chart panel once data is ready
"""

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, html

from components.chart import VISIBLE_STYLE, HIDDEN_STYLE
from utils import ids
from utils.csv_parser import parse_csv
from utils.type_detection import detect_column_types


HERO_VISIBLE: dict = {}
HERO_HIDDEN: dict = {"display": "none"}


@callback(
    Output(ids.CSV_STORE, "data"),
    Output(ids.UPLOAD_STATUS, "children"),
    Output(ids.CHART_PANEL, "style"),
    Output(ids.UPLOAD_WRAPPER, "className"),
    Output(ids.WELCOME_HERO, "style"),
    Input(ids.UPLOAD_DATA, "contents"),
    State(ids.UPLOAD_DATA, "filename"),
    prevent_initial_call=True,
)
def handle_upload(
    contents: str,
    filename: str,
) -> tuple[dict | None, object, dict, str, dict]:
    """
    Triggered when a file is dropped or selected in the upload component.

    Returns:
        - store data (dict with 'records', 'columns', 'col_types', etc.) or None on error
        - compact inline status element shown below the dropzone
        - chart panel style (visible on success, hidden on error)
        - upload wrapper class (anchored on success)
        - welcome hero style (hidden on success)
    """
    if contents is None:
        return None, None, HIDDEN_STYLE, "upload-wrapper", HERO_VISIBLE

    df, error = parse_csv(contents, filename)

    if error:
        feedback = html.Div(
            [
                html.I(className="bi bi-exclamation-triangle-fill me-2"),
                html.Span(error),
            ],
            className="upload-status-error",
        )
        return None, feedback, HIDDEN_STYLE, "upload-wrapper", HERO_VISIBLE

    col_types = detect_column_types(df)

    store_data = {
        "records":   df.to_dict("records"),
        "columns":   list(df.columns),
        "col_types": col_types,
        "filename":  filename,
        "row_count": len(df),
    }

    # Compact one-line success status — replaces the old full-width banner
    num_types = {
        v: sum(1 for t in col_types.values() if t == v)
        for v in set(col_types.values())
    }
    type_summary = "  ·  ".join(
        f"{count} {t}" for t, count in num_types.items()
    )

    feedback = html.Div(
        [
            html.I(className="bi bi-check-circle-fill me-2"),
            html.Span(
                [html.Strong(f"'{filename}'"), f"  ·  {len(df):,} rows  ·  {len(df.columns)} columns"],
            ),
            html.Span(f"  ({type_summary})", className="upload-status-meta"),
        ],
        className="upload-status-inline",
    )

    # "upload-anchored" collapses the padding-top, sliding the card to its layout position.
    # HERO_HIDDEN removes the welcome hero once data is loaded.
    return store_data, feedback, VISIBLE_STYLE, "upload-wrapper upload-anchored", HERO_HIDDEN
