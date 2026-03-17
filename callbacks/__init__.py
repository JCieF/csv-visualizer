"""
callbacks/

All Dash @app.callback definitions for the CSV Data Visualizer.
Callbacks are imported into app.py after the app object is created
to avoid circular import issues.

Planned modules:
    upload.py      — Handle CSV upload, parse, store in dcc.Store
    chart.py       — Update chart based on column/type selections
    filter.py      — Apply filter controls to the active dataset
    theme.py       — Toggle dark mode class on main container
    export.py      — Trigger PNG download of the active chart
"""
