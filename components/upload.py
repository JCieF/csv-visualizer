"""
components/upload.py

CSV file upload dropzone component.
Returns a self-contained Dash layout subtree — no callback logic here.
"""

import dash_bootstrap_components as dbc
from dash import dcc, html

from utils import ids

# Accepted MIME types for the upload widget
ACCEPTED_FILE_TYPES = ".csv"


def create_upload_component() -> dbc.Card:
    """
    Build and return the CSV upload card.

    Contains:
        - A dcc.Upload dropzone styled via the .upload-area CSS class
        - A status div (id=UPLOAD_STATUS) where callbacks write success/error messages
    """
    return dbc.Card(
        dbc.CardBody([
            html.H5("Upload CSV File", className="card-title mb-3"),
            dcc.Upload(
                id=ids.UPLOAD_DATA,
                children=html.Div([
                    html.I(className="bi bi-cloud-upload fs-2 d-block mb-2"),
                    html.Span("Drag and drop or "),
                    html.A("browse to upload", className="text-primary"),
                    html.Br(),
                    html.Small(".csv files only", className="text-muted"),
                ]),
                className="upload-area",
                accept=ACCEPTED_FILE_TYPES,
                multiple=False,
            ),
            # Callback writes success/error feedback here
            html.Div(id=ids.UPLOAD_STATUS, className="mt-3"),
        ]),
        className="mb-4",
    )
