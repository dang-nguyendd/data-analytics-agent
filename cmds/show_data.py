import pandas as pd


def show_table(df, page=1, page_size=20):
    """
    Prepare one page of a DataFrame for display in the AI agent chat.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to display.

    page : int
        Page number, starting from 1.

    page_size : int
        Number of rows per page.

    Returns
    -------
    dict
        Structured table data for the UI.
    """

    # ------------------------------------------------------
    # Validate input
    # ------------------------------------------------------

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "df must be a pandas DataFrame."
        )

    if page < 1:
        raise ValueError(
            "page must be >= 1."
        )

    if page_size < 1:
        raise ValueError(
            "page_size must be >= 1."
        )

    # ------------------------------------------------------
    # Pagination
    # ------------------------------------------------------

    total_rows = len(df)

    total_pages = max(
        1,
        (total_rows + page_size - 1) // page_size
    )

    if page > total_pages:
        raise ValueError(
            f"Page {page} does not exist. "
            f"Total pages: {total_pages}."
        )

    start = (page - 1) * page_size
    end = start + page_size

    display_df = df.iloc[start:end]

    # ------------------------------------------------------
    # Convert values to UI-safe values
    # ------------------------------------------------------

    columns = list(display_df.columns)

    data = []

    for _, row in display_df.iterrows():

        values = []

        for value in row:

            if pd.isna(value):
                values.append(None)
            else:
                values.append(value)

        data.append(values)

    # ------------------------------------------------------
    # Return structured table
    # ------------------------------------------------------

    return {
        "type": "table",
        "columns": columns,
        "data": data,

        "page": page,
        "page_size": page_size,

        "rows": len(data),
        "total_rows": total_rows,

        "total_pages": total_pages,

        "has_previous": page > 1,
        "has_next": page < total_pages,
        "dataframe": df,
    }