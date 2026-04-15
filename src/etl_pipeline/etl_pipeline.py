"""Module defining the ETLProcess abstract base class, which serves as a template for creating specific ETL processes.

This class outlines the structure and methods that any ETL process should implement, including initialization,
data extraction, transformation, and loading.
"""
from abc import ABC, abstractmethod

class ETLPipeline(ABC):
    """Abstract base class for ETL processes.
    """

    # TODO: Implement initialization of a database connection and a logger in the constructor, so that all ETL processes can use them.

    @property
    @abstractmethod
    def process_name(self) -> str:
        """
        Property that returns the name of the ETL process.

        Used for logging and tracking purposes, to identify which ETL process is running or has completed.
        """
        pass

    @abstractmethod
    def init(self) -> None:
        """
        Set up any necessary configurations or resources before starting the ETL process.

        This could include initializing database connections and schemas, ensuring that necessary files or directories
        exist, or any other setup tasks required before the ETL process can begin.
        """
        pass

    @abstractmethod
    def extract(self) -> None:
        """
        Fetch data from one or more sources and prepare it for transformation.

        For example, this could involve making API calls to retrieve data, reading from databases, or
        loading data from files, then store the extracted data in a raw format for further processing.
        """
        pass

    @abstractmethod
    def transform(self) -> None:
        """Process the extracted data.

        For example, this could involve cleaning, normalizing, or enriching the data.
        The transformed data should be in a format that is suitable for loading into the target destination.
        """
        pass

    @abstractmethod
    def load(self) -> None:
        """
        Save the transformed data to the target destination.

        For example, this could involve writing the data to a database, saving it to a file, or sending it to an API.
        """
        pass

    def run(self) -> None:
        """Execute the ETL process in the correct order: init, extract, transform, load."""
        self.init()
        self.extract()
        self.transform()
        self.load()

