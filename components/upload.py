"""
components/upload.py

CSV file upload dropzone component.
Returns a self-contained Dash layout subtree — no callback logic here.
"""

import dash_bootstrap_components as dbc
from dash import dcc, html

from utils import ids

ACCEPTED_FILE_TYPES = ".csv"


def create_upload_component() -> html.Div:
    """
    Build and return the CSV upload section.

    Layout: centered card (~500px wide) with a dashed border dropzone,
    cloud icon, primary CTA, and secondary browse link.
    A compact status line below the card is written by the upload callback.
    """
    return html.Div(
        [
            # Centered card container
            dbc.Card(
                dbc.CardBody(
                    dcc.Upload(
                        id=ids.UPLOAD_DATA,
                        children=html.Div(
                            [
                                # Cloud upload icon
                                html.I(className="bi bi-cloud-upload upload-icon"),

                                # Primary CTA
                                html.P(
                                    "Drag and drop your CSV file",
                                    className="upload-cta-primary",
                                ),

                                # Secondary browse link
                                html.P(
                                    [
                                        "or ",
                                        html.Span(
                                            "click to browse",
                                            className="upload-browse-link",
                                        ),
                                    ],
                                    className="upload-cta-secondary",
                                ),

                                # File type hint
                                html.Small(
                                    ".csv files only",
                                    className="upload-hint",
                                ),
                            ],
                            className="upload-dropzone-inner",
                        ),
                        className="upload-dropzone",
                        accept=ACCEPTED_FILE_TYPES,
                        multiple=False,
                    ),
                    className="p-3",
                ),
                className="upload-card",
            ),

            # Compact one-line status written by handle_upload callback
            html.Div(id=ids.UPLOAD_STATUS, className="upload-status-wrapper"),
        ],
        className="upload-section",
    )
