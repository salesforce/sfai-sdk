import typer
from rich.console import Console
from sfai.constants import ERROR_EMOJI, ERROR_COLOR, SUCCESS_EMOJI, SUCCESS_COLOR
from sfai.app.helm import download_helm_chart

console = Console()

app = typer.Typer(help="Show logs for the current app")


@app.callback(
    invoke_without_command=True, help="Download the helm chart for the current app"
)
def helm_cmd() -> None:
    """
    Download the helm chart for the current app.
    """
    result = download_helm_chart()
    if not result.success:
        console.print(
            f"{ERROR_EMOJI} [{ERROR_COLOR}] unable to download helm chart: "
            f"{result.error}[/]"
        )
        return
    console.print(
        f"{SUCCESS_EMOJI} [{SUCCESS_COLOR}] helm chart downloaded successfully[/]"
    )
