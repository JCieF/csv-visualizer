"""
utils/insights.py

Rule-based data analysis — detects patterns, anomalies, and relationships
in a DataFrame without any external API.

These findings serve two purposes:
  1. Displayed immediately as structured insight cards in the UI.
  2. Passed to utils/gemini_client.py as a compact stats summary so the LLM
     gets pre-computed facts rather than raw data (reduces hallucination risk
     and keeps API payloads small).
"""

from typing import Any

import numpy as np
import pandas as pd

from utils.type_detection import COL_NUMERIC, COL_CATEGORICAL, COL_DATETIME

# ---------------------------------------------------------------------------
# Thresholds — all as named constants, never hardcoded inline
# ---------------------------------------------------------------------------
CORRELATION_THRESHOLD    = 0.70   # |r| above this is a "strong" correlation
OUTLIER_IQR_MULTIPLIER   = 1.5    # standard IQR fence multiplier
OUTLIER_MIN_PCT          = 1.0    # only flag if > 1% of rows are outliers
MISSING_FLAG_PCT         = 5.0    # flag columns with > 5% missing
DOMINANT_CATEGORY_PCT    = 70.0   # flag if one category holds > 70% of rows
SKEW_THRESHOLD           = 1.5    # |skewness| above this is noteworthy
HIGH_CARDINALITY_RATIO   = 0.5    # unique / total > this = likely ID column
MAX_NUMERIC_IN_SUMMARY   = 8      # cap sent to Gemini to keep prompt small
MAX_CATEGORICAL_IN_SUMMARY = 6    # same


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def compute_insights(
    df: pd.DataFrame,
    col_types: dict[str, str],
    filename: str,
) -> dict[str, Any]:
    """
    Run all rule-based checks and return a structured findings dict.

    Returns:
        {
            "filename":  str,
            "rows":      int,
            "columns":   int,
            "findings":  list[dict],   # one dict per detected pattern
            "stats_summary": dict,     # compact stats for Gemini prompt
        }
    """
    findings: list[dict[str, Any]] = []

    _check_missing(df, col_types, findings)
    _check_dominant_categories(df, col_types, findings)
    _check_outliers(df, col_types, findings)
    _check_correlations(df, col_types, findings)
    _check_skewness(df, col_types, findings)
    _check_high_cardinality(df, col_types, findings)

    return {
        "filename":      filename,
        "rows":          len(df),
        "columns":       len(df.columns),
        "findings":      findings,
        "stats_summary": _build_stats_summary(df, col_types, findings, filename),
    }


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def _check_missing(
    df: pd.DataFrame,
    col_types: dict[str, str],
    findings: list,
) -> None:
    """Flag columns with more than MISSING_FLAG_PCT missing values."""
    for col in df.columns:
        pct = df[col].isna().mean() * 100
        if pct > MISSING_FLAG_PCT:
            findings.append({
                "type":    "missing",
                "col":     col,
                "pct":     round(pct, 1),
                "count":   int(df[col].isna().sum()),
            })


def _check_dominant_categories(
    df: pd.DataFrame,
    col_types: dict[str, str],
    findings: list,
) -> None:
    """Flag categorical columns where a single value dominates (> DOMINANT_CATEGORY_PCT)."""
    for col, ctype in col_types.items():
        if ctype != COL_CATEGORICAL:
            continue
        vc = df[col].value_counts(normalize=True)
        if len(vc) == 0:
            continue
        top_pct = vc.iloc[0] * 100
        if top_pct > DOMINANT_CATEGORY_PCT:
            findings.append({
                "type":      "dominant",
                "col":       col,
                "value":     str(vc.index[0]),
                "pct":       round(top_pct, 1),
            })


def _check_outliers(
    df: pd.DataFrame,
    col_types: dict[str, str],
    findings: list,
) -> None:
    """Detect numeric outliers using the IQR fence method."""
    for col, ctype in col_types.items():
        if ctype != COL_NUMERIC:
            continue
        clean = df[col].dropna()
        if len(clean) < 4:  # need enough data for quartiles to be meaningful
            continue
        q1, q3 = clean.quantile(0.25), clean.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        fence_lo = q1 - OUTLIER_IQR_MULTIPLIER * iqr
        fence_hi = q3 + OUTLIER_IQR_MULTIPLIER * iqr
        n_outliers = int(((clean < fence_lo) | (clean > fence_hi)).sum())
        pct = n_outliers / len(df) * 100
        if pct >= OUTLIER_MIN_PCT:
            findings.append({
                "type":    "outlier",
                "col":     col,
                "count":   n_outliers,
                "pct":     round(pct, 1),
            })


def _check_correlations(
    df: pd.DataFrame,
    col_types: dict[str, str],
    findings: list,
) -> None:
    """Find pairs of numeric columns with strong linear correlation."""
    numeric_cols = [c for c, t in col_types.items() if t == COL_NUMERIC]
    if len(numeric_cols) < 2:
        return

    try:
        corr = df[numeric_cols].corr()
    except Exception:
        return

    seen: set[frozenset] = set()
    for i, c1 in enumerate(numeric_cols):
        for c2 in numeric_cols[i + 1:]:
            pair = frozenset({c1, c2})
            if pair in seen:
                continue
            seen.add(pair)
            r = corr.loc[c1, c2]
            if pd.isna(r) or abs(r) < CORRELATION_THRESHOLD:
                continue
            findings.append({
                "type":      "correlation",
                "col1":      c1,
                "col2":      c2,
                "r":         round(float(r), 2),
                "direction": "positive" if r > 0 else "negative",
            })

    # Sort correlations by absolute strength, keep top 3 only
    corr_findings = [f for f in findings if f["type"] == "correlation"]
    non_corr = [f for f in findings if f["type"] != "correlation"]
    corr_findings.sort(key=lambda x: -abs(x["r"]))
    findings.clear()
    findings.extend(non_corr + corr_findings[:3])


def _check_skewness(
    df: pd.DataFrame,
    col_types: dict[str, str],
    findings: list,
) -> None:
    """Flag heavily skewed numeric distributions."""
    for col, ctype in col_types.items():
        if ctype != COL_NUMERIC:
            continue
        clean = df[col].dropna()
        if len(clean) < 10:
            continue
        try:
            skew = float(clean.skew())
        except Exception:
            continue
        if abs(skew) >= SKEW_THRESHOLD:
            findings.append({
                "type":      "skewed",
                "col":       col,
                "skew":      round(skew, 2),
                "direction": "right (positive)" if skew > 0 else "left (negative)",
            })


def _check_high_cardinality(
    df: pd.DataFrame,
    col_types: dict[str, str],
    findings: list,
) -> None:
    """Flag categorical columns that are likely ID/key columns (near-unique values)."""
    for col, ctype in col_types.items():
        if ctype != COL_CATEGORICAL:
            continue
        ratio = df[col].nunique() / max(len(df), 1)
        if ratio >= HIGH_CARDINALITY_RATIO:
            findings.append({
                "type":   "high_cardinality",
                "col":    col,
                "unique": int(df[col].nunique()),
                "ratio":  round(ratio * 100, 1),
            })


# ---------------------------------------------------------------------------
# Compact stats summary for Gemini
# ---------------------------------------------------------------------------

def _build_stats_summary(
    df: pd.DataFrame,
    col_types: dict[str, str],
    findings: list[dict],
    filename: str,
) -> dict[str, Any]:
    """
    Build a compact stats dict (< 600 tokens) to pass to the Gemini prompt.
    Raw rows are never sent — only aggregated statistics.
    """
    numeric_stats = []
    for col, ctype in col_types.items():
        if ctype != COL_NUMERIC:
            continue
        clean = df[col].dropna()
        if len(clean) == 0:
            continue
        numeric_stats.append({
            "name":        col,
            "min":         _fmt(clean.min()),
            "max":         _fmt(clean.max()),
            "mean":        _fmt(clean.mean()),
            "std":         _fmt(clean.std()),
            "missing_pct": round(df[col].isna().mean() * 100, 1),
        })

    cat_stats = []
    for col, ctype in col_types.items():
        if ctype != COL_CATEGORICAL:
            continue
        vc = df[col].value_counts()
        cat_stats.append({
            "name":        col,
            "unique":      int(df[col].nunique()),
            "top_values":  [f"{k} ({v:,})" for k, v in list(vc.items())[:3]],
            "missing_pct": round(df[col].isna().mean() * 100, 1),
        })

    # Translate structured findings to plain English strings for the prompt
    finding_texts = [
        t for t in (_finding_to_text(f) for f in findings[:6]) if t
    ]

    return {
        "filename":             filename,
        "rows":                 len(df),
        "columns":              len(df.columns),
        "numeric_columns":      numeric_stats[:MAX_NUMERIC_IN_SUMMARY],
        "categorical_columns":  cat_stats[:MAX_CATEGORICAL_IN_SUMMARY],
        "detected_findings":    finding_texts,
    }


def _finding_to_text(finding: dict[str, Any]) -> str:
    """Convert a structured finding dict to a plain-English sentence."""
    t = finding.get("type")
    if t == "missing":
        return (
            f"{finding['col']} has {finding['pct']}% missing values "
            f"({finding['count']:,} rows)."
        )
    if t == "dominant":
        return (
            f"In {finding['col']}, '{finding['value']}' accounts for "
            f"{finding['pct']}% of all values."
        )
    if t == "outlier":
        return (
            f"{finding['col']} has {finding['count']:,} outliers "
            f"({finding['pct']}% of rows)."
        )
    if t == "correlation":
        return (
            f"{finding['col1']} and {finding['col2']} have a "
            f"{'strong positive' if finding['r'] > 0 else 'strong negative'} "
            f"correlation (r = {finding['r']})."
        )
    if t == "skewed":
        return (
            f"{finding['col']} is skewed {finding['direction']} "
            f"(skewness = {finding['skew']})."
        )
    if t == "high_cardinality":
        return (
            f"{finding['col']} has {finding['unique']:,} unique values "
            f"({finding['ratio']}% of rows) — may be an ID column."
        )
    return ""


def _fmt(val: Any) -> str:
    """Format a scalar for display in the stats summary."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "N/A"
    if isinstance(val, (int, np.integer)):
        return f"{int(val):,}"
    return f"{float(val):,.2f}"
