from time import sleep

import database_handler
from etl_pipeline.dmi import ETLPipelineDMI
from datetime import datetime
from utils import DATA_DIR
from pathlib import Path
from database_handler import DatabaseHandler


if __name__ == "__main__":
    sleep(5)  # Wait for the database to be ready

    config_file = Path('./local_config.ini')

    database_handler = DatabaseHandler()
    database_handler.connect(config_file)

    print('Running SQL scripts to set up the database schema...')
    list_of_files = list(Path('./scripts/').glob('*.sql'))
    list_of_files.sort()
    for file in list_of_files:
        print(f'Running SQL file: {file.name}')
        database_handler.execute_query(file.read_text())
    print('Database schema set up successfully.')

    etl_process = ETLPipelineDMI(
        data_folder=DATA_DIR,
        configuration=config_file,
        from_date=datetime(2025, 1, 1),
        to_date=datetime(2025, 1, 31),
        stations=['04203']
    )
    etl_process.run()

    print(database_handler.execute_query('SELECT * FROM dim_station LIMIT 5;').fetchall())