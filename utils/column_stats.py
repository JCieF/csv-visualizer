"""
utils/column_stats.py

Compute display-ready statistics for a single DataFrame column.
Used by the column summary card component.

All functions are pure (no Dash imports) and safe to unit-test.
"""

from typing import Any, Optional

import numpy as np
import pandas as pd

from utils.type_detection import COL_CATEGORICAL, COL_DATETIME, COL_NUMERIC


def compute_column_stats(
    df: pd.DataFrame,
    col: str,
    col_type: str,
) -> dict[str, Any]:
    """
    Return a display-ready stats dictionary for one column.

    Common keys (all types):
        column, type, total, null_count, null_pct, valid_pct,
        donut_values, donut_labels, center_text

    Type-specific keys:
        Numeric:     min, max, mean, median
        Categorical: unique_count, top_items  (list of {label, count})
        Datetime:    date_min, date_max, date_range_days
    """
    series = df[col]
    total = len(series)
    null_count = int(series.isna().sum())
    non_null = total - null_count
    null_pct = round(null_count / total * 100, 1) if total > 0 else 0.0
    valid_pct = round(100.0 - null_pct, 1)

    stats: dict[str, Any] = {
        "column":     col,
        "type":       col_type,
        "total":      total,
        "null_count": null_count,
        "null_pct":   null_pct,
        "valid_pct":  valid_pct,
    }

    if col_type == COL_NUMERIC:
        _add_numeric_stats(stats, series)

    elif col_type == COL_CATEGORICAL:
        _add_categorical_stats(stats, series, total, null_count)
        return stats  # donut already set inside helper

    else:  # COL_DATETIME (or unrecognised — treated like datetime)
        _add_datetime_stats(stats, series)

    # Shared completeness donut for numeric + datetime
    if null_count > 0:
        stats["donut_values"] = [non_null, null_count]
        stats["donut_labels"] = ["Valid", "Missing"]
    else:
        stats["donut_values"] = [non_null]
        stats["donut_labels"] = ["Valid"]

    stats["center_text"] = f"{valid_pct:.0f}%<br>valid"
    return stats


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _add_numeric_stats(stats: dict[str, Any], series: pd.Series) -> None:
    clean = series.dropna()
    stats["min"]    = _fmt_number(clean.min())    if len(clean) else "—"
    stats["max"]    = _fmt_number(clean.max())    if len(clean) else "—"
    stats["mean"]   = _fmt_number(clean.mean())   if len(clean) else "—"
    stats["median"] = _fmt_number(clean.median()) if len(clean) else "—"


def _add_categorical_stats(
    stats: dict[str, Any],
    series: pd.Series,
    total: int,
    null_count: int,
) -> None:
    unique_count = int(series.nunique())
    top = series.value_counts().head(4)

    stats["unique_count"] = unique_count
    stats["top_items"] = [
        {"label": str(k), "count": int(v)} for k, v in top.items()
    ]

    # Build donut slices: top categories + Other + Missing
    donut_values: list[int] = list(top.values)
    donut_labels: list[str] = [str(k) for k in top.index]

    other = total - null_count - int(top.sum())
    if other > 0:
        donut_values.append(other)
        donut_labels.append("Other")
    if null_count > 0:
        donut_values.append(null_count)
        donut_labels.append("Missing")

    stats["donut_values"] = donut_values
    stats["donut_labels"] = donut_labels
    stats["center_text"]  = f"{unique_count}<br>unique"


def _add_datetime_stats(stats: dict[str, Any], series: pd.Series) -> None:
    clean = pd.to_datetime(series.dropna(), errors="coerce").dropna()
    if len(clean):
        date_min = clean.min()
        date_max = clean.max()
        stats["date_min"]        = date_min.strftime("%Y-%m-%d")
        stats["date_max"]        = date_max.strftime("%Y-%m-%d")
        stats["date_range_days"] = (date_max - date_min).days
    else:
        stats["date_min"]        = "—"
        stats["date_max"]        = "—"
        stats["date_range_days"] = 0


def _fmt_number(val: Any) -> str:
    """Format a scalar for display — integers without decimals, floats to 2 dp."""
    if val is None:
        return "—"
    try:
        if np.isnan(val):
            return "—"
    except (TypeError, ValueError):
        pass
    if isinstance(val, (int, np.integer)):
        return f"{int(val):,}"
    if isinstance(val, float) and val == int(val):
        return f"{int(val):,}"
    return f"{float(val):,.2f}"
