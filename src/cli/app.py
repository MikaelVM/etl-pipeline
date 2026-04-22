from typer import Typer
from commands import dmi_etl_app, test_app


app = Typer(
    context_settings={
        "help_option_names": ["-h", "--help"]
    }
)

app.add_typer(dmi_etl_app, name="dmi")
app.add_typer(test_app, name="test")

if __name__ == "__main__":
    app()