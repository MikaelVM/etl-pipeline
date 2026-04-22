from typer import Argument, Option, Typer

app = Typer(
)

@app.command(
    'run'
)
def run_etl():
    """Run the entire ETL process."""
    from etl_pipeline.dmi import ETLPipelineDMI
    from utils import DATA_DIR

    etl_pipeline = ETLPipelineDMI(
        DATA_DIR
    )
    etl_pipeline.run()
