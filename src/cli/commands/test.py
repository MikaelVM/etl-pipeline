from typer import Argument, Option, Typer

app = Typer(
)

@app.command(
    'hello'
)
def hello(
    name: str = Argument(..., help="Your name")
):
    """Say hello to the user."""
    print(f"Hello, {name}!")