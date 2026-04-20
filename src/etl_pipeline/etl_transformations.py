"""
Module containing transformations that are standard across multiple ETL processes.

For example, transformations that are commonly used for cleaning and normalizing data, such as removing duplicate rows,
normalizing JSON columns, or dropping unnecessary columns.
"""
from transformer import DataFrameTransformation
import pandas as pd

class RemoveDuplicateRows(DataFrameTransformation):
    """A transformation that removes duplicate rows from a DataFrame."""

    def transform(self, data_frame: pd.DataFrame) -> pd.DataFrame:

        try:
            data_frame = data_frame.drop_duplicates()
        except TypeError:
            # Can't drop duplicates because the DataFrame contains unhashable types (e.g., lists or dictionaries).
            # Indices of duplicate rows are istead found by using a string representation of the rows.
            data_frame = data_frame.loc[data_frame.astype(str).drop_duplicates().index]

        return data_frame


class DropColumns(DataFrameTransformation):
    """A transformation that drops specified columns from a DataFrame.

    Attributes:
        columns_to_drop (list[str]): A list of column names to be dropped from the DataFrame.
    """

    def __init__(self, columns_to_drop: list[str]):
        self.columns_to_drop = columns_to_drop

    def transform(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        data_frame = data_frame.drop(columns=self.columns_to_drop)
        return data_frame


class RenameColumns(DataFrameTransformation):
    """A transformation that renames specified columns in a DataFrame.

    Attributes:
        columns_to_rename (dict[str, str]): A dictionary mapping old column names to new column names.
    """

    def __init__(self, *, columns_to_rename: dict[str, str]):
        self.columns_to_rename = columns_to_rename

    def transform(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        if not all(column in data_frame.columns for column in self.columns_to_rename.keys()):
            missing_columns = [column for column in self.columns_to_rename.keys() if column not in data_frame.columns]
            raise ValueError(f"Columns {missing_columns} not found in DataFrame.")

        data_frame = data_frame.rename(columns=self.columns_to_rename)
        return data_frame


class SplitColumn(DataFrameTransformation):
    """A transformation that splits a column containing lists into multiple columns, one for each element in the list."""

    def __init__(self, *, column_to_split: str, new_column_headers: list[str], drop_original_column: bool = True):
        self.column_to_split = column_to_split
        self.new_column_titles = new_column_headers
        self.drop_original_column = drop_original_column

    def transform(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        if self.column_to_split not in data_frame.columns:
            raise ValueError(f"Column '{self.column_to_split}' not found in DataFrame.")

        data_frame[self.new_column_titles] = data_frame[self.column_to_split].apply(pd.Series)

        if self.drop_original_column:
            data_frame.drop(columns=[self.column_to_split], inplace=True)

        return data_frame
