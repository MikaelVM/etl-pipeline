import json
from pathlib import Path
from typing import Any


class JSONHandler:
    @staticmethod
    def write_json(*, file_path: Path, data: dict[str, Any], makedir:bool = False) -> None:
        """Saves a dictionary as a JSON file.

        Args:
            data (dict): The dictionary to be saved as JSON.
            file_path (Path): The path where the JSON file will be saved.
            makedir (bool): Whether to create the parent directory if it does not exist. Defaults to False.
        """
        if not file_path.parent.exists():
            if makedir:
                file_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                raise FileNotFoundError(f"The directory '{file_path.parent}' does not exist.")

        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

    @staticmethod
    def read_json(*, file_path: Path) -> dict[str, Any]:
        """Loads a JSON file and returns its content as a dictionary.

        Args:
            file_path (Path): The path to the JSON file to be loaded.
        """
        with open(file_path, 'r') as json_file:
            return json.load(json_file)