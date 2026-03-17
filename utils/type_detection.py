"""
utils/type_detection.py

Infers the semantic type of each column in a Pandas DataFrame.
Types are kept as simple string labels so they can be JSON-serialised
and stored in dcc.Store alongside the data.
"""

import pandas as pd

# Column type labels — use these constants everywhere, never raw strings
COL_NUMERIC = "numeric"
COL_CATEGORICAL = "categorical"
COL_DATETIME = "datetime"

# If a column has fewer unique values than this fraction of total rows,
# treat it as categorical even if it looks numeric (e.g. zip codes, IDs)
CATEGORICAL_UNIQUENESS_THRESHOLD = 0.05


def detect_column_types(df: pd.DataFrame) -> dict[str, str]:
    """
    Infer the semantic type of each column in the DataFrame.

    Returns:
        A dict mapping column name → one of COL_NUMERIC, COL_CATEGORICAL,
        COL_DATETIME.
    """
    col_types: dict[str, str] = {}

    for col in df.columns:
        col_types[col] = _infer_type(df[col])

    return col_types


def _infer_type(series: pd.Series) -> str:
    """Infer the type of a single column series."""

    # Already parsed as datetime by pandas
    if pd.api.types.is_datetime64_any_dtype(series):
        return COL_DATETIME

    # Already parsed as numeric by pandas
    if pd.api.types.is_numeric_dtype(series):
        return COL_NUMERIC

    # For object columns: try to parse as datetime before falling back
    if series.dtype == object:
        try:
            pd.to_datetime(series, infer_datetime_format=True)
            return COL_DATETIME
        except (ValueError, TypeError):
            pass

    return COL_CATEGORICAL


def get_columns_by_type(
    col_types: dict[str, str], target_type: str
) -> list[str]:
    """
    Filter column names by their detected type.

    Args:
        col_types: Output of detect_column_types().
        target_type: One of COL_NUMERIC, COL_CATEGORICAL, COL_DATETIME.

    Returns:
        List of column names matching the target type.
    """
    return [col for col, t in col_types.items() if t == target_type]
