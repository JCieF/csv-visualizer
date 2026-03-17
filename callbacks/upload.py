"""
callbacks/upload.py

Handles the CSV file upload event:
  1. Parses the file via utils.csv_parser
  2. Detects column types via utils.type_detection
  3. Serialises the DataFrame + metadata to JSON and stores it in dcc.Store
  4. Shows success or error feedback in the upload status div
  5. Reveals the chart panel once data is ready
"""

import json

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, html

from components.chart import VISIBLE_STYLE, HIDDEN_STYLE
from utils import ids
from utils.csv_parser import parse_csv
from utils.type_detection import detect_column_types


@callback(
    Output(ids.CSV_STORE, "data"),
    Output(ids.UPLOAD_STATUS, "children"),
    Output(ids.CHART_PANEL, "style"),
    Input(ids.UPLOAD_DATA, "contents"),
    State(ids.UPLOAD_DATA, "filename"),
    prevent_initial_call=True,
)
def handle_upload(
    contents: str,
    filename: str,
) -> tuple[dict | None, object, dict]:
    """
    Triggered when a file is dropped or selected in the upload component.

    Returns:
        - store data (dict with 'records' and 'col_types') or None on error
        - feedback element shown below the dropzone
        - chart panel style (visible on success, hidden on error)
    """
    if contents is None:
        return None, None, HIDDEN_STYLE

    df, error = parse_csv(contents, filename)

    if error:
        feedback = dbc.Alert(error, color="danger", dismissable=True)
        return None, feedback, HIDDEN_STYLE

    # Detect column types and store alongside the data
    col_types = detect_column_types(df)

    # Serialise to JSON — dcc.Store accepts plain dicts
    store_data = {
        "records": df.to_dict("records"),
        "columns": list(df.columns),
        "col_types": col_types,
        "filename": filename,
        "row_count": len(df),
    }

    feedback = dbc.Alert(
        [
            html.Strong(f"'{filename}' uploaded successfully. "),
            f"{len(df):,} rows · {len(df.columns)} columns",
        ],
        color="success",
        dismissable=True,
    )

    return store_data, feedback, VISIBLE_STYLE
