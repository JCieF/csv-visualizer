"""
components/insights_panel.py

Key Insights panel layout.

Structure:
  ┌─────────────────────────────────────────────────────┐
  │  💡 Key Insights                  [Gemini Flash ✦]  │
  ├─────────────────────────────────────────────────────┤
  │  Rule-based findings (one row per detected pattern) │
  │  ─────────────── AI Analysis ──────────────         │
  │  [dcc.Loading spinner]  or  Gemini narrative text   │
  └─────────────────────────────────────────────────────┘

The panel starts hidden and is revealed by the insights callback.
"""

import dash_bootstrap_components as dbc
from dash import dcc, html

from utils import ids

# ---------------------------------------------------------------------------
# Finding type → visual config
# ---------------------------------------------------------------------------

_FINDING_CONFIG: dict[str, dict[str, str]] = {
    "correlation":    {"icon": "bi-arrow-left-right", "color": "#6366f1", "label": "Correlation"},
    "outlier":        {"icon": "bi-exclamation-circle-fill", "color": "#f97316", "label": "Outliers"},
    "missing":        {"icon": "bi-question-circle-fill", "color": "#f59e0b", "label": "Missing Data"},
    "dominant":       {"icon": "bi-bar-chart-fill", "color": "#0d9488", "label": "Dominant Value"},
    "skewed":         {"icon": "bi-distribute-horizontal", "color": "#8b5cf6", "label": "Skewed"},
    "high_cardinality": {"icon": "bi-collection-fill", "color": "#06b6d4", "label": "High Cardinality"},
}

_DEFAULT_CONFIG = {"icon": "bi-info-circle-fill", "color": "#64748b", "label": "Note"}


# ---------------------------------------------------------------------------
# Finding card builder (called from the callback, not statically)
# ---------------------------------------------------------------------------

def build_finding_row(finding: dict) -> html.Div:
    """Render a single rule-based finding as a labelled row."""
    cfg = _FINDING_CONFIG.get(finding.get("type", ""), _DEFAULT_CONFIG)
    color = cfg["color"]

    description = _describe_finding(finding)
    if not description:
        return html.Div()

    return html.Div(
        [
            # Colored icon badge
            html.Span(
                html.I(className=f"bi {cfg['icon']}"),
                className="finding-icon-badge",
                style={"backgroundColor": color, "color": "#fff"},
            ),
            # Finding text
            html.Span(description, className="finding-text"),
            # Type label pill
            html.Span(cfg["label"], className="finding-type-pill",
                      style={"color": color, "borderColor": color}),
        ],
        className="finding-row",
        style={"borderLeftColor": color},
    )


def _describe_finding(f: dict) -> str:
    """Turn a structured finding dict into a human-readable sentence."""
    t = f.get("type")
    if t == "correlation":
        direction = "positively" if f["r"] > 0 else "negatively"
        strength = "very strongly" if abs(f["r"]) >= 0.9 else "strongly"
        return (
            f"{f['col1']} and {f['col2']} are {strength} {direction} "
            f"correlated (r = {f['r']})."
        )
    if t == "outlier":
        return (
            f"{f['col']} contains {f['count']:,} outliers "
            f"({f['pct']}% of rows)."
        )
    if t == "missing":
        return (
            f"{f['col']} has {f['pct']}% missing values "
            f"({f['count']:,} rows affected)."
        )
    if t == "dominant":
        return (
            f"'{f['value']}' makes up {f['pct']}% of all values in {f['col']}."
        )
    if t == "skewed":
        return (
            f"{f['col']} has a {f['direction']} skew "
            f"(skewness = {f['skew']}). Consider log-transforming before modelling."
        )
    if t == "high_cardinality":
        return (
            f"{f['col']} has {f['unique']:,} unique values ({f['ratio']}% of rows) "
            f"— likely an identifier column."
        )
    return ""


# ---------------------------------------------------------------------------
# Static panel skeleton (populated dynamically by callbacks)
# ---------------------------------------------------------------------------

def create_insights_panel() -> html.Div:
    """
    Return the insights panel outer container.
    Initially hidden; the rule-based callback reveals it and populates content.
    """
    return html.Div(
        id=ids.INSIGHTS_PANEL,
        style={"display": "none"},
        children=[
            dbc.Card(
                dbc.CardBody([

                    # ── Panel header ──────────────────────────────────────
                    html.Div([
                        html.Div([
                            html.I(className="bi bi-lightbulb-fill me-2 insights-header-icon"),
                            html.Span("Key Insights"),
                        ], className="section-header mb-0 border-0 pb-0"),

                        # Gemini badge — only visible when AI key is set
                        html.Span(
                            [
                                html.I(className="bi bi-stars me-1"),
                                "Gemini Flash",
                            ],
                            id=ids.INSIGHTS_GEMINI_BADGE,
                            className="gemini-badge",
                            style={"display": "none"},   # shown by callback if key present
                        ),
                    ], className="d-flex align-items-center justify-content-between mb-3"),

                    # ── Rule-based findings (populated by callback) ───────
                    html.Div(
                        id=ids.INSIGHTS_RULE_CONTENT,
                        className="insights-findings-list",
                    ),

                    # ── AI narrative section ──────────────────────────────
                    html.Div(
                        [
                            html.Div(className="insights-ai-divider"),
                            dcc.Loading(
                                html.Div(
                                    id=ids.INSIGHTS_AI_CONTENT,
                                    className="insights-ai-text",
                                ),
                                type="dot",
                                color="var(--color-accent)",
                                className="insights-ai-loader",
                            ),
                        ],
                        id=ids.INSIGHTS_AI_SECTION,
                        style={"display": "none"},   # shown by callback if API key is set
                    ),

                ]),
                className="insights-card mb-0",
            )
        ],
        className="mb-0",
    )
