"""ETL pipeline implementation for fetching and processing meteorological data from the DMI API."""

from pathlib import Path
from typing import Any, Optional
from datetime import datetime
import calendar
from concurrent.futures import ThreadPoolExecutor
# TODO: Future Work - Ensure this function is the best choice for determining the number of available CPU cores across
#  different platforms and environments.
from multiprocessing import cpu_count

import httpx
from pydantic import BaseModel
import pandas as pd
from src.etl_pipeline import ETLPipeline, StationFeatureCollection, ObservationFeatureCollection
from src.json import JSONHandler
from src.utils import DATA_DIR


class ETLPipelineDMI(ETLPipeline):
    """
    ETL pipeline for fetching and processing meteorological data from the DMI API.

    Attributes:
        process_name (str): The name of the ETL process.
        json_handler (JSONHandler): An instance of the JSONHandler class for reading and writing JSON files.
        data_folder (Path): The path to the folder where data files will be stored.
        from_date (datetime): The starting date for fetching data from the DMI API. Defaults to None.
        to_date (datetime): The ending date for fetching data from the DMI API. Defaults to None.
        stations (list[str]): A list of station IDs to fetch data for. Defaults to None (meaning all stations).
    """

    def __init__(
            self,
            data_folder: Path,
            *,
            from_date: datetime = None,
            to_date: datetime = None,
            stations: list[str] = None
    ):
        """
        Initialize the ETLPipelineDMI with the specified data folder.

        Args:
            data_folder (Path): The path to the folder where data files will be stored.
        """
        super().__init__()
        self.json_handler = JSONHandler()
        self.data_folder = data_folder
        self.from_date = from_date
        self.to_date = to_date
        self.stations = stations

    @property
    def process_name(self) -> str:
        """Return the name of the ETL process."""
        return "DMI ETL Process"

    @property
    def stations(self) -> list[str] | None:
        """Return the list of station IDs to fetch data for."""
        return self._stations

    @stations.setter
    def stations(self, station_ids: list[str]) -> None:
        """Set the list of station IDs to fetch data for.

        Args:
            station_ids (list[str]): A list of station IDs to fetch data for.
        """
        if station_ids is None:
            self._stations = None
            return

        if not isinstance(station_ids, list):
            raise ValueError("Stations must be provided as a list of strings.")

        for station_id in station_ids:
            if not station_id.isdigit():
                raise ValueError(f"Invalid station ID: {station_id}. Station IDs must be numeric strings.")

        for station_id in station_ids:
            if len(station_id) != 5:
                raise ValueError(f"Invalid station ID: {station_id}. Station IDs must be 5 digits long.")

        self._stations = station_ids

    def init(self) -> None:
        """
        Initialization process of the DMI ETL pipeline.

        TODO: Finish writing documentation for this method once the implementation is complete.
        FIXME: Remove from abstract base class and split initialization steps into separate methods that are called
         in each section of the ETL process (e.g., init_extract, init_transform, init_load) to avoid unnecessary
         initialization of resources that are only needed for specific sections of the pipeline.
        """
        # Extract
        raw_folder = self.data_folder / 'raw'
        dmi_station_folder = raw_folder / 'dmi_stations'
        dmi_observation_folder = raw_folder / 'dmi_observations'

        if not raw_folder.exists():
            raw_folder.mkdir()

        if not dmi_station_folder.exists():
            dmi_station_folder.mkdir()

        if not dmi_observation_folder.exists():
            dmi_observation_folder.mkdir()

        # Transform
        staging_folder = self.data_folder / 'staging'
        processed_folder = self.data_folder / 'processed'

        if not staging_folder.exists():
            staging_folder.mkdir()

        if not processed_folder.exists():
            processed_folder.mkdir()

        # Load
        # TODO: Add database initialization and logging.

    def extract(self) -> None:
        """
        Extraction process of the DMI ETL pipeline.

        This method is responsible for fetching data from the DMI API for both station information and observations.
        """
        self.extract_stations()

        self.extract_observations()

    def extract_stations(self) -> None:
        """
        Fetch station data from the DMI API and save the JSON response to a file.

        Parameters are ignored, as fetching all the station data from the DMI API is not expected to be a
        time-consuming operation.

        TODO: Future Work - Implement filtering of station data based on the specified station IDs.
        """
        file_path = self.data_folder / 'raw' / 'dmi_stations' / 'all.json'
        if file_path.exists():
            print("Skipping API request for station data - Data already exists.")
            return

        api_endpoint = 'https://opendataapi.dmi.dk/v2/metObs/collections/station/items'

        station_json = self._fetch_api_data(
            api_endpoint=api_endpoint,
            validation_model=StationFeatureCollection,
            params={'limit': 100000}  # Highest limit allowed by the DMI API.
        )

        self.json_handler.write_json(
            file_path=file_path,
            data=station_json
        )

    def extract_observations(self) -> None:
        """Fetch meteorological observation data from the DMI API and save the JSON response to a file."""
        api_endpoint = 'https://opendataapi.dmi.dk/v2/metObs/collections/observation/items'
        # TODO: Future Work - Allow user configuration of the number of worker threads to use for fetching data.
        available_cpu_cores = cpu_count() - 1  # Leave one core free to avoid overloading the system.

        # If no specific station IDs are provided, fetch data for all stations by reading from the station data file.
        if self.stations is None:
            # FIXME: File path used twice across methods in class, should be defined as a class attribute or constant.
            dmi_station_file = self.data_folder / 'raw' / 'dmi_stations' / 'all.json'
            if not dmi_station_file.exists():
                raise FileNotFoundError("Station data file not found. Please provide a list of station IDs or ensure that the station data file exists.")

            station_json = self.json_handler.read_json(file_path=dmi_station_file)

            # Remove duplicates and sort station IDs.
            station_ids = list(set(feature['properties']['stationId'] for feature in station_json['features']))
            station_ids.sort()
        else:
            station_ids = self.stations

        for station_id in station_ids:
            for year in range(self.from_date.year, self.to_date.year + 1):
                for month in range(
                        self.from_date.month if year == self.from_date.year else 1,
                        self.to_date.month + 1 if year == self.to_date.year else 13):
                    print(f"Fetching data for station {station_id} for year {year}, month {month}...")

                    with ThreadPoolExecutor(max_workers=available_cpu_cores) as executor:
                        for day in range(
                                1,
                                (calendar.monthrange(year, month)[1] + 1) if
                                (year != self.to_date.year or month != self.to_date.month)
                                else (self.to_date.day + 1)
                        ):
                            executor.submit(
                                self._fetch_observation,
                                api_endpoint,
                                station_id,
                                datetime(year, month, day, 0, 0, 0),
                                datetime(year, month, day, 23, 59, 59)
                            )


    def _fetch_observation(self, api_endpoint: str, station_id: str, from_time: datetime, to_time: datetime) -> None:
        api_params = {
            'stationId': station_id,
            'datetime': self._construct_datetime_argument(from_time, to_time),
            'limit': 100000 # Highest limit allowed by the DMI API, minimizing number of API requests.
        }

        while True:
            file_path = self.data_folder / 'raw' / 'dmi_observations' / f'station_{station_id}' / f'{from_time.year}' / f'{from_time.month:02d}' / f'{from_time.day:02d}_p{api_params.get("offset", 0) // api_params["limit"] + 1}.json'

            if file_path.exists():
                print(f"Skipping API request (Station: {station_id}, Date: {from_time.date()}) - Data already exists.")
                api_params['offset'] = api_params.get('offset', 0) + api_params['limit']
                continue

            response_json = self._fetch_api_data(
                api_endpoint=api_endpoint,
                validation_model=ObservationFeatureCollection,
                params=api_params
            )

            if response_json['numberReturned'] == 0:
                break

            self.json_handler.write_json(
                file_path=file_path,
                data=response_json,
                makedir=True
            )

            api_params['offset'] = api_params.get('offset', 0) + api_params['limit']


    @staticmethod
    def _construct_datetime_argument(
            from_time: Optional[datetime] = None,
            to_time: Optional[datetime] = None
    ) -> str | None:
        """Constructs a datetime argument string based on the provided from_time and to_time.

        Args:
            from_time (Optional[datetime]): The starting datetime. Defaults to None.
            to_time (Optional[datetime]): The ending datetime. Defaults to None.
        """

        if from_time is None and to_time is None:
            return None

        if from_time is not None and to_time is None:
            return f"{from_time.isoformat()}Z"

        if from_time is None and to_time is not None:
            return f"{to_time.isoformat()}Z"

        return f"{from_time.isoformat()}Z/{to_time.isoformat()}Z"


    @staticmethod
    def _fetch_api_data(
            *,
            api_endpoint: str,
            timeout: float = 10.0,
            validation_model: type[BaseModel],
            params: dict[str, Any] = None
    ) -> dict:
        """Fetch data from API endpoint with validation of the response using a Pydantic model.

        Args:
            api_endpoint (str): The URL of the API endpoint to fetch data from.
            timeout (float): The maximum time to wait for a response from the API, in seconds. Defaults to 10.0 seconds.
            validation_model (type[BaseModel]): A Pydantic model class that defines the expected structure and data
            types of the API response.
            params (dict[str, Any], optional): A dictionary of query parameters to be sent with the API request.
            Defaults to None.

        Returns:
            dict: The JSON response from the API.
        """
        response = httpx.get(
            url=api_endpoint,
            timeout=timeout,
            params=params
        )

        # Raise an exception if the API request was unsuccessful (e.g., status code is not 200)
        response.raise_for_status()

        response_json = response.json()

        # Validate the JSON response to ensure it has the expected structure and data types.
        validation_model.model_validate(response_json)

        return response_json

    def transform(self) -> None:
        """Transformation process of the DMI ETL pipeline."""
        self.transform_stations()
        self.transform_observations()

    def transform_stations(self) -> None:
        station_json = self.json_handler.read_json(file_path=self.data_folder / 'raw' / 'dmi_stations' / 'all.json')

        dmi_stations_dataframe = pd.json_normalize(station_json['features'])

        pass

    def transform_observations(self) -> None:
        pass

    def load(self) -> None:
        pass


if __name__ == "__main__":
    etl_process = ETLPipelineDMI(
        DATA_DIR,
        from_date=datetime(2025, 1, 1),
        to_date=datetime(2025, 12, 31),
        stations=['04202', '04203', '04205', '04208']
    )
    etl_process.run()