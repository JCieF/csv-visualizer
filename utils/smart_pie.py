"""
utils/smart_pie.py

Smart pie chart handler — manages pie charts with high cardinality data.

Rules:
  - If a column has > CARDINALITY_PIE_MAX unique values:
      → suggest switching to a horizontal bar chart
  - If a column has > PIE_TOP_N unique values but ≤ CARDINALITY_PIE_MAX:
      → limit the pie to top PIE_TOP_N categories and group the rest as "Other"
  - Otherwise render the pie as normal
"""

from typing import Optional

import pandas as pd

# Beyond this many unique values, bar chart is a better fit than pie
CARDINALITY_PIE_MAX = 15

# Number of categories to show in a pie; the rest are collapsed into "Other"
PIE_TOP_N = 10

# Label used for the collapsed remainder slice
OTHER_LABEL = "Other"


def prepare_pie_data(
    df: pd.DataFrame,
    names_col: str,
    values_col: Optional[str] = None,
    top_n: int = PIE_TOP_N,
) -> pd.DataFrame:
    """
    Limit a DataFrame to the top N categories in names_col, combining
    any remaining categories into a single "Other" row.

    Args:
        df:         Source DataFrame.
        names_col:  Column used as pie slice labels.
        values_col: Column used as pie slice sizes. If None, value counts are used.
        top_n:      Maximum number of slices before grouping into "Other".

    Returns:
        A new DataFrame with at most top_n + 1 rows, suitable for px.pie().
        Returns the original DataFrame unchanged if it already has ≤ top_n categories.
    """
    if values_col:
        # Aggregate by summing numeric values per category
        grouped = (
            df.groupby(names_col)[values_col]
            .sum()
            .sort_values(ascending=False)
        )
        value_label = values_col
    else:
        # Fall back to counting occurrences
        grouped = df[names_col].value_counts()
        value_label = "count"

    if len(grouped) <= top_n:
        # No truncation needed — return data in a normalised format
        result = grouped.reset_index()
        result.columns = [names_col, value_label]
        return result

    top = grouped.head(top_n)
    other_sum = grouped.iloc[top_n:].sum()

    result = top.reset_index()
    result.columns = [names_col, value_label]

    other_row = pd.DataFrame([{names_col: OTHER_LABEL, value_label: other_sum}])
    return pd.concat([result, other_row], ignore_index=True)


def get_pie_status(
    df: pd.DataFrame,
    x_col: str,
    current_chart_type: str,
) -> tuple[str, Optional[str]]:
    """
    Assess whether a pie chart is appropriate for the given column.

    Args:
        df:                 Source DataFrame.
        x_col:              The column selected for pie labels.
        current_chart_type: The currently selected chart type string.

    Returns:
        (status, message) where status is one of:
          "ok"       — pie is fine, no action needed
          "truncated" — pie will be shown with top-N + Other grouping
          "suggest_bar" — too many categories, bar chart recommended
        message is a human-readable explanation (None when status is "ok").
    """
    if current_chart_type != "pie":
        return "ok", None

    unique_count = df[x_col].nunique()

    if unique_count > CARDINALITY_PIE_MAX:
        return (
            "suggest_bar",
            (
                f"'{x_col}' has {unique_count:,} unique values — "
                f"too many for a readable pie chart. "
                f"A horizontal bar chart will show all values more clearly."
            ),
        )

    if unique_count > PIE_TOP_N:
        return (
            "truncated",
            (
                f"'{x_col}' has {unique_count:,} unique values. "
                f"Displaying the top {PIE_TOP_N} categories; "
                f"the rest are grouped as \"{OTHER_LABEL}\"."
            ),
        )

    return "ok", None
