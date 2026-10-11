import pandas as pd

# ==========================================================
# Data Summary
# ==========================================================

def data_summary(df):
    """
    Summarize a data file.

    Parameters
    ----------
    df: DataFrame object

    Returns
    -------
    dict
        Dictionary containing:
        - column headers
        - data types
        - first 3 rows
        - row and column counts
    """

    # ------------------------------------------------------
    # Validate input
    # ------------------------------------------------------
    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "df must be a pandas DataFrame."
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
        "shape": {"rows": df.shape[0], "columns": df.shape[1]},
        "columns": headers,
        "dtypes": dtypes,
        "first_3_rows": first_3_rows,
    }