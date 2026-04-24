from multiprocessing import connection

from sqlalchemy import create_engine, text
from configparser import ConfigParser
from pathlib import Path

class DatabaseHandler:
    def __init__(self):
        self.engine = None

    def connect(self, configuration: Path | str):
        """Establish a connection to the PostgreSQL database using configuration from a file.

        Args:
            configuration (Path | str): 
        """
        if isinstance(configuration, str):
            self.engine = create_engine(configuration)
        elif isinstance(configuration, Path):
            config = ConfigParser()
            config.read(configuration)

            db_config = config['DATABASE']
            user = db_config['user']
            password = db_config['password']
            host = db_config['host']
            port = db_config['port']
            database = db_config['database']

            self.engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}")
        else:
            raise Exception("")

    def execute_query(self, query: str):
        if self.engine is None:
            raise Exception("Database connection not established. Call connect() first.")

        connection = self.engine.connect()

        try:
            result = connection.execute(text(query))
            connection.commit()
            return result
        finally:
            connection.close()