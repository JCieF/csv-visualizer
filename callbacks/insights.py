"""
callbacks/insights.py

Two-step insights pipeline:

  Step 1 — fast (rule-based):
    Input:  CSV_STORE data
    Output: INSIGHTS_RULE_STORE, INSIGHTS_RULE_CONTENT, INSIGHTS_PANEL visibility,
            INSIGHTS_AI_SECTION visibility, INSIGHTS_GEMINI_BADGE visibility

  Step 2 — slow (Gemini):
    Input:  INSIGHTS_RULE_STORE data
    Output: INSIGHTS_AI_CONTENT (narrative text)

Separating them means rule-based cards appear immediately while the AI
section shows a loading spinner until Gemini responds (~1–2 s).
"""

import os
from typing import Optional

import pandas as pd
from dash import Input, Output, State, callback, html
import dash_bootstrap_components as dbc

from utils import ids
from utils.insights import compute_insights
from utils.gemini_client import generate_insights
from components.insights_panel import build_finding_row

_VISIBLE = {"display": "block"}
_HIDDEN  = {"display": "none"}
_FLEX    = {"display": "flex"}


# ---------------------------------------------------------------------------
# Step 1 — Rule-based (fires as soon as CSV is uploaded)
# ---------------------------------------------------------------------------

@callback(
    Output(ids.INSIGHTS_RULE_STORE, "data"),
    Output(ids.INSIGHTS_RULE_CONTENT, "children"),
    Output(ids.INSIGHTS_PANEL, "style"),
    Output(ids.INSIGHTS_AI_SECTION, "style"),
    Output(ids.INSIGHTS_GEMINI_BADGE, "style"),
    Input(ids.CSV_STORE, "data"),
)
def compute_rule_insights(
    store_data: Optional[dict],
) -> tuple:
    """
    Compute and display rule-based findings immediately after upload.
    Also controls whether the AI section is shown (requires GOOGLE_API_KEY).
    """
    if store_data is None:
        return None, [], _HIDDEN, _HIDDEN, _HIDDEN

    try:
        df       = pd.DataFrame.from_records(store_data["records"])
        result   = compute_insights(df, store_data.get("col_types", {}), store_data.get("filename", "dataset"))
        findings = result.get("findings", [])

        if not findings:
            no_findings = html.P(
                "No significant patterns detected in this dataset.",
                className="text-muted fst-italic small mb-0",
            )
            finding_elements = [no_findings]
        else:
            finding_elements = [build_finding_row(f) for f in findings]

        # Show AI section only if the API key is available
        has_key       = bool(os.environ.get("GOOGLE_API_KEY", "").strip())
        ai_style      = _VISIBLE if has_key else _HIDDEN
        badge_style   = _FLEX   if has_key else _HIDDEN

        return result, finding_elements, _VISIBLE, ai_style, badge_style

    except Exception:
        return None, [], _HIDDEN, _HIDDEN, _HIDDEN


# ---------------------------------------------------------------------------
# Step 2 — Gemini narrative (fires when rule store is populated)
# ---------------------------------------------------------------------------

@callback(
    Output(ids.INSIGHTS_AI_CONTENT, "children"),
    Input(ids.INSIGHTS_RULE_STORE, "data"),
)
def generate_ai_narrative(
    rule_data: Optional[dict],
) -> list:
    """
    Call Gemini Flash with the compact stats summary and render the narrative.
    Returns an empty list if the API key is missing or the call fails —
    the dcc.Loading spinner will simply disappear.
    """
    if rule_data is None:
        return []

    stats_summary = rule_data.get("stats_summary", {})
    if not stats_summary:
        return []

    narrative = generate_insights(stats_summary)

    if not narrative:
        return []

    # Parse the numbered lines and render each as a paragraph
    paragraphs = []
    for line in narrative.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        paragraphs.append(
            html.P(line, className="ai-insight-line mb-2"),
        )

    if not paragraphs:
        return []

    return [
        html.Div(paragraphs, className="ai-insights-body"),
    ]
