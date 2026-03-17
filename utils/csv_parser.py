"""
utils/csv_parser.py

Handles decoding and parsing of CSV files uploaded via dcc.Upload.
dcc.Upload delivers file contents as a base64-encoded data URI string,
e.g.: "data:text/csv;base64,<encoded_bytes>"
"""

import base64
import io
from typing import Optional

import pandas as pd

# Encodings to try in order when UTF-8 fails
FALLBACK_ENCODINGS = ["latin-1", "cp1252"]

# Maximum number of rows allowed for upload (guards against huge files)
MAX_ROWS = 100_000


def parse_csv(contents: str, filename: str) -> tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Decode a base64 CSV upload and return a parsed DataFrame.

    Args:
        contents: Base64 data URI string from dcc.Upload.
        filename: Original filename, used to validate extension.

    Returns:
        (DataFrame, None)  on success.
        (None, error_msg)  on any failure.
    """
    if not filename.lower().endswith(".csv"):
        return None, f'"{filename}" is not a CSV file. Please upload a .csv file.'

    try:
        # Split "data:<mime>;base64,<data>" — we only need the data part
        _, content_string = contents.split(",", 1)
        decoded_bytes = base64.b64decode(content_string)
    except Exception:
        return None, "Could not decode the uploaded file. It may be corrupted."

    # Try UTF-8 first, fall back to other encodings for files from Excel etc.
    df: Optional[pd.DataFrame] = None
    for encoding in ["utf-8"] + FALLBACK_ENCODINGS:
        try:
            df = pd.read_csv(io.StringIO(decoded_bytes.decode(encoding)))
            break
        except UnicodeDecodeError:
            continue
        except pd.errors.EmptyDataError:
            return None, "The uploaded CSV file is empty."
        except pd.errors.ParserError as e:
            return None, f"Could not parse the CSV file: {e}"

    if df is None:
        return None, "Could not read the file. Try saving it as UTF-8 CSV and re-uploading."

    if df.empty or len(df.columns) == 0:
        return None, "The CSV file has no data or no column headers."

    if len(df) > MAX_ROWS:
        return None, (
            f"The file has {len(df):,} rows, which exceeds the {MAX_ROWS:,} row limit. "
            "Please upload a smaller file."
        )

    return df, None
