"""
components/column_summary.py

Column summary card layout.

Each card contains:
  - Bold colored header bar  (column name + type badge)
  - Donut chart              (Plotly, transparent background)
  - Four bullet stats        (type-appropriate: min/max/mean/missing, top categories, or date range)
  - Matching colored footer bar
  - Light-tinted body background matching the header accent

Accent color cycles through CARD_SCHEMES (orange → teal → red → green → repeat).
"""

from typing import Any

import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import dcc, html

from utils import ids
from utils.type_detection import COL_NUMERIC, COL_CATEGORICAL, COL_DATETIME

# ---------------------------------------------------------------------------
# Color schemes — one per "slot", cycling with card_index % len(CARD_SCHEMES)
# ---------------------------------------------------------------------------
CARD_SCHEMES: list[dict[str, str]] = [
    {
        "gradient": "linear-gradient(135deg, #f97316, #fb923c)",
        "accent":   "#f97316",
        "light":    "#fff7ed",
        "border":   "#fed7aa",
    },  # orange
    {
        "gradient": "linear-gradient(135deg, #0d9488, #14b8a6)",
        "accent":   "#0d9488",
        "light":    "#f0fdfa",
        "border":   "#99f6e4",
    },  # teal
    {
        "gradient": "linear-gradient(135deg, #ef4444, #f87171)",
        "accent":   "#ef4444",
        "light":    "#fef2f2",
        "border":   "#fecaca",
    },  # red
    {
        "gradient": "linear-gradient(135deg, #22c55e, #4ade80)",
        "accent":   "#22c55e",
        "light":    "#f0fdf4",
        "border":   "#bbf7d0",
    },  # green
]

# Vivid multi-color palette for categorical donut slices
_CATEGORICAL_COLORS: list[str] = [
    "#6366f1", "#f59e0b", "#10b981", "#3b82f6",
    "#a78bfa", "#f43f5e", "#14b8a6", "#fb923c",
]

# Cap cards at this many columns to avoid overwhelming the UI
MAX_DISPLAY_COLUMNS = 20


# ---------------------------------------------------------------------------
# Donut chart builder
# ---------------------------------------------------------------------------

def _build_donut_figure(stats: dict[str, Any], scheme: dict[str, str]) -> go.Figure:
    """
    Build a transparent donut (ring) chart for a column.

    Numeric / Datetime:  two slices — Valid (accent) and Missing (soft gray)
    Categorical:         up to 4+ slices using a vivid multi-color palette
    """
    values: list = stats.get("donut_values", [1])
    labels: list = stats.get("donut_labels", [""])
    center_text: str = stats.get("center_text", "")

    is_categorical = stats["type"] == COL_CATEGORICAL

    if is_categorical:
        colors = _CATEGORICAL_COLORS[: len(values)]
    else:
        # Valid = accent color,  Missing = neutral semi-transparent gray
        # The neutral works on both light and dark card backgrounds
        colors = [scheme["accent"], "rgba(148,163,184,0.35)"][: len(values)]

    fig = go.Figure(
        go.Pie(
            values=values,
            labels=labels,
            hole=0.62,
            marker=dict(colors=colors, line=dict(width=0)),
            textinfo="none",
            hoverinfo="label+percent+value",
            direction="clockwise",
        )
    )

    # Center annotation inside the donut hole
    fig.add_annotation(
        text=center_text,
        x=0.5, y=0.5,
        font=dict(
            size=13,
            color=scheme["accent"],
            family="Inter, system-ui, -apple-system, sans-serif",
        ),
        showarrow=False,
        align="center",
    )

    fig.update_layout(
        margin=dict(t=4, b=4, l=4, r=4),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        height=160,
    )
    return fig


# ---------------------------------------------------------------------------
# Bullet stats list builder
# ---------------------------------------------------------------------------

def _build_bullet_stats(stats: dict[str, Any], scheme: dict[str, str]) -> html.Ul:
    """
    Build four bullet stat rows appropriate for the column type.
    Categorical cards pad to exactly 4 rows so all cards share a consistent height.
    """
    col_type = stats["type"]
    accent = scheme["accent"]

    if col_type == COL_NUMERIC:
        bullets = [
            ("Min",     stats.get("min",    "—")),
            ("Max",     stats.get("max",    "—")),
            ("Mean",    stats.get("mean",   "—")),
            ("Missing", f"{stats['null_count']:,} ({stats['null_pct']}%)"),
        ]

    elif col_type == COL_CATEGORICAL:
        top_items = stats.get("top_items", [])
        bullets = [(item["label"], f"{item['count']:,}") for item in top_items[:4]]
        # Pad to 4 rows so card heights stay uniform
        while len(bullets) < 4:
            bullets.append(("—", "—"))

    else:  # COL_DATETIME
        bullets = [
            ("Earliest", stats.get("date_min",        "—")),
            ("Latest",   stats.get("date_max",        "—")),
            ("Range",    f"{stats.get('date_range_days', 0):,} days"),
            ("Missing",  f"{stats['null_count']:,} ({stats['null_pct']}%)"),
        ]

    items = [
        html.Li(
            [
                html.Span(label, className="stat-label"),
                html.Span(value, className="stat-value"),
            ],
            className="stat-bullet",
            style={"borderLeftColor": accent},
        )
        for label, value in bullets
    ]

    return html.Ul(items, className="stat-bullets")


# ---------------------------------------------------------------------------
# Public card builder
# ---------------------------------------------------------------------------

def build_column_card(stats: dict[str, Any], card_index: int) -> dbc.Col:
    """
    Assemble a full column stat card wrapped in a responsive dbc.Col.

    Responsive breakpoints:
        xs=12 → 1 per row on mobile
        sm=6  → 2 per row on tablet
        lg=3  → 4 per row on desktop
    """
    scheme = CARD_SCHEMES[card_index % len(CARD_SCHEMES)]
    type_label = stats["type"].title()

    card = dbc.Card(
        [
            # ── Gradient header bar ─────────────────────────────────────
            html.Div(
                [
                    html.Span(stats["column"], className="stat-card-col-name"),
                    html.Span(type_label, className="stat-card-type-badge"),
                ],
                className="stat-card-header",
                style={"background": scheme["gradient"]},
            ),

            # ── Body: donut chart + bullet stats ────────────────────────
            dbc.CardBody(
                [
                    dcc.Graph(
                        figure=_build_donut_figure(stats, scheme),
                        config={"displayModeBar": False},
                        className="stat-card-donut",
                    ),
                    _build_bullet_stats(stats, scheme),
                ],
                className="stat-card-body",
                style={"backgroundColor": scheme["light"]},
            ),

            # ── Matching gradient footer bar ─────────────────────────────
            html.Div(
                className="stat-card-footer",
                style={"background": scheme["gradient"]},
            ),
        ],
        className="stat-card h-100",
        style={"borderColor": scheme["border"]},
    )

    # --i drives the staggered CSS animation delay (50 ms × card index)
    return dbc.Col(
        card,
        xs=12, sm=6, lg=3,
        className="mb-4 stat-card-col",
        style={"--i": str(card_index)},
    )


# ---------------------------------------------------------------------------
# Section container (initially hidden, revealed by callback)
# ---------------------------------------------------------------------------

def create_column_summary_section() -> html.Div:
    """
    Outer container for the column summary cards.
    Starts hidden; render_column_summary populates children and sets display:block.
    """
    return html.Div(
        id=ids.COLUMN_SUMMARY,
        style={"display": "none"},
        className="mb-2",
    )
