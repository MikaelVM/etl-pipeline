from src.etl_process import ETLProcess

class ETLProcessDMI(ETLProcess):
    def __init__(self):
        super().__init__()

    @property
    def process_name(self) -> str:
        return "DMI ETL Process"

    def init(self) -> None:
        pass

    def extract(self) -> None:
        pass

    def transform(self) -> None:
        pass

    def load(self) -> None:
        pass

