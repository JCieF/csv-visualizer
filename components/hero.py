"""
components/hero.py

Welcome hero section — shown in the empty state before any CSV is uploaded.
Communicates the app's purpose and capabilities at a glance.
Hidden by the upload callback once data is loaded.
"""

from dash import html

from utils import ids

# Feature pills: (Bootstrap icon class, label)
FEATURE_PILLS: list[tuple[str, str]] = [
    ("bi bi-bar-chart-fill", "Bar charts"),
    ("bi bi-graph-up", "Line charts"),
    ("bi bi-pie-chart-fill", "Pie charts"),
    ("bi bi-circle", "Scatter plots"),
    ("bi bi-stars", "AI Insights"),
    ("bi bi-moon-fill", "Dark mode"),
]


def create_welcome_hero() -> html.Div:
    """
    Build the welcome hero shown before any CSV is uploaded.
    Returns a self-contained layout subtree with no callback logic.
    """
    pills = [
        html.Span(
            [html.I(className=f"{icon} me-1"), label],
            className="hero-feature-pill",
        )
        for icon, label in FEATURE_PILLS
    ]

    return html.Div(
        [
            html.H1("CSV Visualizer", className="hero-title"),
            html.P(
                [
                    "Drop any CSV and explore your data instantly — ",
                    html.Br(),
                    "auto-detected columns, interactive charts, and AI-powered insights.",
                ],
                className="hero-tagline",
            ),
            html.Div(pills, className="hero-feature-pills"),
        ],
        id=ids.WELCOME_HERO,
        className="welcome-hero",
    )
