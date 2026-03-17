"""
utils/

Helper functions and shared utilities for the CSV Data Visualizer.
All functions here are pure (no Dash dependencies) to keep them
easy to test and reuse.

Planned modules:
    csv_parser.py      — Load and validate CSV files with Pandas
    type_detection.py  — Infer column types (numeric, categorical, datetime)
    chart_builder.py   — Build Plotly figure objects from DataFrame + config
    data_filters.py    — Apply filter criteria to a Pandas DataFrame
"""
