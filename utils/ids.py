"""
utils/ids.py

Single source of truth for all Dash component IDs.
Import this module in both components/ and callbacks/ so that
ID strings are never duplicated as raw literals.
"""

# --- Stores ---
CSV_STORE = "csv-store"
THEME_STORE = "theme-store"

# --- Upload ---
UPLOAD_DATA = "upload-data"
UPLOAD_STATUS = "upload-status"

# --- Chart panel ---
CHART_PANEL = "chart-panel"
CHART_TYPE = "chart-type"
X_AXIS = "x-axis"
Y_AXIS = "y-axis"
CHART_GRAPH = "chart-graph"
CHART_SUGGESTION = "chart-suggestion"
CHART_SUGGESTION_BTN = "chart-suggestion-btn"

# --- Column summary section ---
COLUMN_SUMMARY = "column-summary"

# --- Upload wrapper (drives centered → anchored transition) ---
UPLOAD_WRAPPER = "upload-wrapper"

# --- Theme toggle ---
DARK_MODE_TOGGLE  = "dark-mode-toggle"
THEME_TOGGLE_ICON = "theme-toggle-icon"

# --- Insights panel ---
INSIGHTS_PANEL        = "insights-panel"
INSIGHTS_RULE_STORE   = "insights-rule-store"
INSIGHTS_RULE_CONTENT = "insights-rule-content"
INSIGHTS_AI_CONTENT   = "insights-ai-content"
INSIGHTS_AI_SECTION   = "insights-ai-section"
INSIGHTS_GEMINI_BADGE = "insights-gemini-badge"

# --- App shell ---
MAIN_CONTAINER = "main-container"
