from pathlib import Path

import pandas as pd


# ==========================================================
# Data Summary
# ==========================================================

def data_summary(data_file_dir):
    """
    Summarize a CSV or Parquet data file.

    Parameters
    ----------
    data_file_dir : str or Path
        Path to the CSV or Parquet file.

    Returns
    -------
    dict
        Dictionary containing:
        - file information
        - column headers
        - data types
        - first 3 rows
    """

    # ------------------------------------------------------
    # Validate path
    # ------------------------------------------------------

    path = Path(data_file_dir)

    if not path.exists():
        raise FileNotFoundError(
            f"Data file not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {path}"
        )

    # ------------------------------------------------------
    # Read data
    # ------------------------------------------------------

    suffix = path.suffix.lower()

    if suffix == ".csv":

        df = pd.read_csv(path)

    elif suffix == ".parquet":

        df = pd.read_parquet(path)

    else:

        raise ValueError(
            "Unsupported file type. "
            "Only CSV and Parquet files are supported."
        )

    # ------------------------------------------------------
    # Headers
    # ------------------------------------------------------

    headers = list(df.columns)

    # ------------------------------------------------------
    # Data types
    # ------------------------------------------------------

    dtypes = {
        column: str(dtype)
        for column, dtype in df.dtypes.items()
    }

    # ------------------------------------------------------
    # First 3 rows
    # ------------------------------------------------------

    first_3_rows = (
        df.head(3)
        .to_dict(orient="records")
    )

    # ------------------------------------------------------
    # Return result
    # ------------------------------------------------------

    return {
        "file": str(path),
        "filename": path.name,
        "format": suffix.replace(".", ""),
        "columns": headers,
        "dtypes": dtypes,
        "first_3_rows": first_3_rows,
    }