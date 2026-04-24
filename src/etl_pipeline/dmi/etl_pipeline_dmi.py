"""ETL pipeline implementation for fetching and processing meteorological data from the DMI API."""

import calendar
from concurrent.futures import ThreadPoolExecutor
# TODO: Future Work - Ensure this function is the best choice for determining the number of available CPU cores across
#  different platforms and environments.
from datetime import datetime
from multiprocessing import cpu_count
from pathlib import Path
from time import sleep
from typing import Any, Optional

import httpx
import pandas as pd

from database_handler import DatabaseHandler
from etl_pipeline import ETLPipeline
from etl_pipeline.dmi import StationFeatureCollection, ObservationFeatureCollection
from etl_pipeline.etl_transformations import DropColumns, RemoveDuplicateRows, RenameColumns, SplitColumn
from pydantic import BaseModel
from transformer import DataFrameTransformer
from utils import DATA_DIR, read_json, write_json


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
            *,
            data_folder: Path,
            configuration: Path | str,
            from_date: datetime = None,
            to_date: datetime = None,
            stations: list[str] = None
    ):
        """
        Initialize the ETLPipelineDMI with the specified data folder.

        Args:
            data_folder (Path): The path to the folder where data files will be stored.
            configuration (Path | str): The path to the configuration file for database connection or connection string.
            from_date (datetime, optional): The starting date for fetching data from the DMI API. Defaults to None.
            to_date (datetime, optional): The ending date for fetching data from the DMI API. Defaults to None.
            stations (list[str], optional): A list of station IDs to fetch data for.
             Defaults to None (meaning all stations).
        """
        super().__init__()
        self.data_folder = data_folder
        self.configuration = configuration
        self.from_date = from_date
        self.to_date = to_date
        self.stations = stations
        self.database_handler = DatabaseHandler()

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

        Raises:
            ValueError: If station_ids is not a list of strings,
             or if any station ID is not a numeric string of 5 digits.
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

    def extract(self) -> None:
        """
        Extract process of the DMI ETL pipeline.

        This method is responsible for fetching data from the DMI API for both station information and observations.
        """
        raw_folder = self.data_folder / 'raw'
        dmi_station_folder = raw_folder / 'dmi_stations'
        dmi_observation_folder = raw_folder / 'dmi_observations'

        if not raw_folder.exists():
            raw_folder.mkdir()

        if not dmi_station_folder.exists():
            dmi_station_folder.mkdir()

        if not dmi_observation_folder.exists():
            dmi_observation_folder.mkdir()

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

        write_json(
            file_path=file_path,
            data=station_json
        )

    def extract_observations(self) -> None:
        """Fetch meteorological observation data from the DMI API and save the JSON response to a file.

        FIXME: To complex (7)
        """
        # TODO: Future Work - Allow a configuration with the number of worker threads to use for fetching data.
        available_cpu_cores = cpu_count() - 1  # Leave one core free to avoid overloading the system.

        # If no specific station IDs are provided, fetch data for all stations by reading from the station data file.
        if self.stations is None:
            # FIXME: File path used twice across methods in class, should be defined as a class attribute or constant.
            dmi_station_file = self.data_folder / 'raw' / 'dmi_stations' / 'all.json'
            if not dmi_station_file.exists():
                raise FileNotFoundError("Station data file not found. Please provide a list of station IDs or ensure that the station data file exists.")

            station_json = read_json(file_path=dmi_station_file)

            # Remove duplicates and sort station IDs.
            station_ids = list(set(feature['properties']['stationId'] for feature in station_json['features']))
            station_ids.sort()

        else:
            for station_id in self.stations:
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
                                    station_id,
                                    datetime(year, month, day, 0, 0, 0),
                                    datetime(year, month, day, 23, 59, 59)
                                )


    def _fetch_observation(self, station_id: str, from_time: datetime, to_time: datetime) -> None:
        """Fetch observation data for a specific station and time range and save the JSON response to a file.

        Args:
            api_endpoint (str): The URL of the DMI API endpoint for fetching observation data.
            station_id (str): The ID of the station to fetch data for.
            from_time (datetime): The starting datetime for fetching data.
            to_time (datetime): The ending datetime for fetching data.
        """
        api_endpoint = 'https://opendataapi.dmi.dk/v2/metObs/collections/observation/items'
        limit = 100000  # Highest limit allowed by the DMI API, minimizing number of API requests.
        api_params = {
            'stationId': station_id,
            'datetime': self._construct_datetime_argument(from_time, to_time),
            'limit': limit,
            'offset': 0
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

            write_json(
                file_path=file_path,
                data=response_json,
                makedir=True
            )

            api_params['offset'] += limit

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
        print(f"Fetching data from API endpoint: {api_endpoint} with parameters: {params}...")
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
        processed_folder = self.data_folder / 'processed'

        if not processed_folder.exists():
            processed_folder.mkdir()

        self.transform_stations()
        self.transform_observations()

    def transform_stations(self) -> None:
        station_json = read_json(file_path=self.data_folder / 'raw' / 'dmi_stations' / 'all.json')

        dmi_stations_dataframe = pd.json_normalize(station_json['features'])

        dmi_stations_transformer = DataFrameTransformer(transformations=[
            DropColumns(
                columns_to_drop=['id', 'type', 'geometry.type']
            ),
            SplitColumn(
                column_to_split='geometry.coordinates',
                new_column_headers=['longitude', 'latitude']
            ),
            RenameColumns(
                columns_to_rename={
                'properties.stationId': 'station_id',
                'properties.wmoStationId': 'wmo_station_id',
                'properties.regionId': 'region_id',
                'properties.name': 'name',
                'properties.owner': 'owner',
                'properties.country': 'country',
                'properties.wmoCountryCode': 'wmo_county_code',
                'properties.anemometerHeight': 'anemometer_height',
                'properties.barometerHeight': 'barometer_height',
                'properties.stationHeight': 'station_height',
                'properties.operationFrom': 'operation_from',
                'properties.parameterId': 'parameter_id',
                'properties.created': 'created',
                'properties.validFrom': 'valid_from',
                'properties.validTo': 'valid_to',
                'properties.operationTo': 'operation_to',
                'properties.type': 'type',
                'properties.updated': 'updated',
                'properties.status': 'status'
                }
            ),
            RemoveDuplicateRows()
        ])

        dmi_stations_dataframe = dmi_stations_transformer.transform(dmi_stations_dataframe)

        if not (self.data_folder / 'processed' / 'dmi_stations').exists():
            (self.data_folder / 'processed' / 'dmi_stations').mkdir(parents=True)

        dmi_stations_dataframe.to_csv(self.data_folder / 'processed' / 'dmi_stations' / 'all.csv', index=False)


    def transform_observations(self) -> None:
        for file in (self.data_folder / 'raw' / 'dmi_observations').rglob('*.json'):
            print(f"Transforming observation data from file: {file}")
            self._transform_observation_file(file)


    def _transform_observation_file(self, file_path: Path) -> None:
        target_folder = self.data_folder / 'processed' / 'dmi_observations' / file_path.parent.relative_to(self.data_folder / 'raw' / 'dmi_observations')

        observation_dataframe = pd.json_normalize(read_json(file_path=file_path)['features'])

        dmi_observations_transformer = DataFrameTransformer(transformations=[
            DropColumns(
                columns_to_drop=['id','type', 'geometry.type']
            ),
            SplitColumn(
                column_to_split='geometry.coordinates',
                new_column_headers=['longitude', 'latitude']
            ),
            RenameColumns(
                columns_to_rename={
                    'properties.parameterId': 'type',
                    'properties.created': 'created',
                    'properties.value': 'value',
                    'properties.observed': 'observed',
                    'properties.stationId': 'station_id',
                }
            ),
            RemoveDuplicateRows(),
        ])

        observation_dataframe = dmi_observations_transformer.transform(observation_dataframe)

        if not target_folder.exists():
            target_folder.mkdir(parents=True)
        observation_dataframe.to_csv(target_folder / file_path.with_suffix('.csv').name, index=False)

    def load(self) -> None:
        self.database_handler.connect(self.configuration)
        self.load_stations()
        self.load_observations()

    def load_stations(self) -> None:
        for station_file in (self.data_folder / 'processed' / 'dmi_stations').glob('*.csv'):
            

            print(f"Loading station data from file: {station_file}")


        pass

    def load_observations(self) -> None:
        pass


if __name__ == "__main__":
    sleep(10)

    etl_process = ETLPipelineDMI(
        DATA_DIR,
        from_date=datetime(2025, 1, 1),
        to_date=datetime(2025, 1, 31),
        stations=['04203']
    )
    etl_process.run()