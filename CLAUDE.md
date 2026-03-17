# CLAUDE.md

---

## Project Context

### Overview
A web-based CSV Data Visualizer built with Python and Plotly Dash. Users can upload any CSV file and instantly explore their data through interactive charts, filtering controls, and a data preview table — all without writing code.

### Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Framework | [Plotly Dash](https://dash.plotly.com/) >= 2.14 | Reactive web app framework |
| UI Components | [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/) >= 1.5 | Layout, styling, dark mode |
| Data Handling | [Pandas](https://pandas.pydata.org/) >= 2.1 | CSV parsing, filtering, transformation |
| Charts | [Plotly](https://plotly.com/python/) >= 5.18 | Bar, line, pie, scatter charts |
| Language | Python 3.9+ | — |

### Features
- CSV file upload with validation and error feedback
- Automatic column type detection (numeric, categorical, datetime)
- Chart type selector: Bar, Line, Pie, Scatter
- Dynamic X/Y axis field selectors driven by detected column types
- Filtering panel with range sliders (numeric) and dropdowns (categorical)
- Dark mode toggle (persisted in `dcc.Store`)
- Export active chart as PNG
- Responsive data preview table

### Architecture

```
csv-visualizer/
├── app.py                  # Entry point: Dash app init, layout, callback imports
├── requirements.txt        # Python dependencies
│
├── assets/
│   └── custom.css          # Design tokens (CSS vars) + dark mode overrides
│
├── components/             # Reusable layout builders (return Dash component trees)
│   ├── __init__.py
│   ├── upload.py           # File upload dropzone
│   ├── chart.py            # Chart display panel
│   ├── filter_panel.py     # Filtering controls
│   ├── data_table.py       # Data preview table
│   └── navbar.py           # Top nav + dark mode toggle
│
├── callbacks/              # All @app.callback definitions
│   ├── __init__.py
│   ├── upload.py           # Parse CSV → store in dcc.Store
│   ├── chart.py            # Render chart from store + selections
│   ├── filter.py           # Apply filters to dataset
│   ├── theme.py            # Toggle dark mode CSS class
│   └── export.py           # PNG download trigger
│
└── utils/                  # Pure helper functions (no Dash dependencies)
    ├── __init__.py
    ├── csv_parser.py       # Load and validate CSV with Pandas
    ├── type_detection.py   # Infer column types
    ├── chart_builder.py    # Build Plotly figures from DataFrame + config
    └── data_filters.py     # Apply filter criteria to a DataFrame
```

**Data flow:**
1. User uploads CSV → `callbacks/upload.py` parses it with Pandas → stores JSON in `dcc.Store`
2. User picks chart type + axes → `callbacks/chart.py` reads the store, calls `utils/chart_builder.py`, renders figure
3. User adjusts filters → `callbacks/filter.py` filters the DataFrame, triggers chart re-render
4. Dark mode toggle → `callbacks/theme.py` adds/removes `.dark-mode` CSS class on `#main-container`

---

## Coding Guidelines

1. **Python 3.9+** — Use features available in 3.9 and above (e.g., `list[str]` type hints, `|` union types are 3.10+, avoid those).

2. **Clean, readable code with comments on complex logic** — Straightforward code needs no comment. When the *why* is not obvious (e.g., a Pandas quirk, a Dash callback constraint), add a short inline comment explaining it.

3. **Handle all errors gracefully with try/except blocks** — Never let an unhandled exception crash the app. Catch specific exceptions, log the error, and return a user-friendly message or a safe fallback value.

4. **Use type hints for function parameters and return values** — Every function signature should declare input and output types. Example:
   ```python
   def detect_column_type(series: pd.Series) -> str:
       ...
   ```

5. **Follow PEP 8 style guide** — Max line length 88 chars (Black-compatible). Use `snake_case` for functions and variables, `PascalCase` for classes, `UPPER_CASE` for module-level constants.

6. **Create reusable components** — Each component function should accept only what it needs as parameters and return a self-contained Dash layout tree. Avoid embedding hardcoded IDs in deeply nested structures — define component IDs as module-level constants.

7. **Optimize for performance** — Use `dcc.Store` to cache parsed DataFrames as JSON (avoid re-parsing on every callback). Use `pandas` vectorized operations instead of row-by-row loops. Limit chart render to the filtered dataset only.

8. **Never use hardcoded values** — Colors, sizes, chart type names, column type labels, and any other configuration values must be defined as named constants at the top of their module (or in a dedicated `config.py`), never inline.

---

> **CRITICAL — Git Policy:**
> NEVER run `git commit`, `git push`, or any destructive git command unless the user **explicitly** says to do so. Always ask for permission first. This applies to all git operations including staging, committing, pushing, branching, and resetting.
