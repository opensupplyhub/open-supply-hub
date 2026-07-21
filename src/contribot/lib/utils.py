from typing import List


def map_n_dataframe_cols_to_excel_cols(n: int) -> List[str]:
    """
    Generate Excel-style column labels for a given number of sequential columns.
    Excel column naming follows a base-26 alphabetic system:
        - 1 → "A"
        - 2 → "B"
        - ...
        - 26 → "Z"
        - 27 → "AA"
        - 28 → "AB"
        - ...
        and so on.
    This function returns a list of such labels from "A" up to the label
    corresponding to the nth column. The length of the returned list
    will be equal to `n`.
    Parameters
    ----------
    n : int
        Number of columns to map. Must be >= 1.
    Returns
    -------
    List[str]
        A list of Excel-style column labels of length `n`.
    Notes
    -----
    This is useful when working with wide DataFrames and writing them
    to Excel files that require explicit column-letter references.
    """
    result = []
    for i in range(n):
        col = ""
        num = i
        while num >= 0:
            col = chr(ord("A") + (num % 26)) + col
            num = num // 26 - 1
        result.append(col)
    return result
