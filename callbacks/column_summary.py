"""
callbacks/column_summary.py

Renders column summary cards inside a collapsible accordion whenever new CSV
data is loaded.  The accordion is collapsed by default so the chart panel is
the primary visible focus after upload.
"""

from typing import Optional

import pandas as pd
from dash import Input, Output, callback, html
import dash_bootstrap_components as dbc

from utils import ids
from utils.column_stats import compute_column_stats
from components.column_summary import build_column_card, MAX_DISPLAY_COLUMNS

_VISIBLE = {"display": "block"}
_HIDDEN  = {"display": "none"}


@callback(
    Output(ids.COLUMN_SUMMARY, "children"),
    Output(ids.COLUMN_SUMMARY, "style"),
    Input(ids.CSV_STORE, "data"),
)
def render_column_summary(
    store_data: Optional[dict],
) -> tuple[list, dict]:
    """
    Build one stat card per column (capped at MAX_DISPLAY_COLUMNS) and
    wrap them in a collapsed dbc.Accordion.

    The accordion starts closed so the chart panel is immediately visible
    after upload.  Users can expand it on demand.
    """
    if store_data is None:
        return [], _HIDDEN

    try:
        df             = pd.DataFrame.from_records(store_data["records"])
        col_types      = store_data.get("col_types", {})
        all_columns    = store_data["columns"]
        visible        = all_columns[:MAX_DISPLAY_COLUMNS]
        truncated      = len(all_columns) > MAX_DISPLAY_COLUMNS

        cards = [
            build_column_card(
                compute_column_stats(df, col, col_types.get(col, "categorical")),
                card_index=i,
            )
            for i, col in enumerate(visible)
        ]

        truncation_notice = (
            [
                dbc.Alert(
                    [
                        html.I(className="bi bi-info-circle me-2"),
                        f"Showing the first {MAX_DISPLAY_COLUMNS} of "
                        f"{len(all_columns)} columns.",
                    ],
                    color="info",
                    className="mb-3",
                    dismissable=True,
                )
            ]
            if truncated
            else []
        )

        # Dynamic title showing column count as a pill badge
        accordion_title = html.Span(
            [
                html.I(className="bi bi-table me-2"),
                "Column Summary",
                dbc.Badge(
                    f"{len(visible)} columns",
                    color="primary",
                    pill=True,
                    className="ms-2 summary-count-badge",
                ),
            ],
            className="d-flex align-items-center",
        )

        accordion = dbc.Accordion(
            [
                dbc.AccordionItem(
                    children=[*truncation_notice, dbc.Row(cards, className="g-3")],
                    title=accordion_title,
                    class_name="summary-accordion-item",
                ),
            ],
            start_collapsed=True,
            className="column-summary-accordion",
        )

        return [accordion], _VISIBLE

    except (KeyError, ValueError, TypeError):
        return [], _HIDDEN
