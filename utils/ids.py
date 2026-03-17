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

# --- App shell ---
MAIN_CONTAINER = "main-container"
