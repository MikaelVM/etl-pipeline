"""Module defining the DataFrameTransformer class.

The DataFrameTransformer class is designed to apply a series of transformations to a pandas DataFrame
in a specified order.

Each transformation is an instance of a class that implements the DataFrameTransformation interface,
which requires a transform method that takes a DataFrame as input and returns a transformed DataFrame.
"""
from abc import ABC, abstractmethod

import pandas as pd


class DataFrameTransformer():
    """A class that applies a series of transformations to a DataFrame.

    Attributes:
        transformations (list[DataFrameTransformation]): A list of transformations to be applied to the DataFrame,
         in the order they should be applied.
    """

    def __init__(self, transformations: list[DataFrameTransformation]):
        """Initialize the DataFrameTransformer with a list of transformations.

        Args:
            transformations (list[DataFrameTransformation]): A list of transformations to be applied to the DataFrame,
             in the order they should be applied.
        """
        self.transformations = transformations

    def transform(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        """Apply transformations to the input DataFrame in the order they were provided.

        Args:
            data_frame (pd.DataFrame): The input DataFrame to be transformed.
        """
        for transformation in self.transformations:
            data_frame = transformation.transform(data_frame)
        return data_frame


class DataFrameTransformation(ABC):
    """Interface for a transformation that can be applied to a DataFrame."""

    @abstractmethod
    def transform(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        """Transform the input DataFrame and returns the transformed DataFrame.

        Args:
            data_frame (pd.DataFrame): The input DataFrame to be transformed.
        """
        pass
