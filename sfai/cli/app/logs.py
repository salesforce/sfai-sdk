import typer
from typing import Optional
from rich.console import Console
from sfai.constants import ERROR_EMOJI, ERROR_COLOR
from sfai.app.logs import logs

console = Console()

app = typer.Typer(help="Show logs for the current app")


@app.callback(invoke_without_command=True, help="Show logs for the current app")
def logs_cmd(
    platform: Optional[str] = typer.Option(None, help="Platform to show logs from"),
    environment: Optional[str] = typer.Option(
        None, help="Environment to show logs from"
    ),
) -> None:
    """
    Show logs for the current app.

    Args:
        platform: Optional[str]
            Platform to show logs from
        environment: str
            Environment to show logs from (defaults to "default")
    """

    result = logs(platform=platform, environment=environment)
    if not result.success:
        console.print(
            f"{ERROR_EMOJI} [{ERROR_COLOR}] unable to fetch logs: {result.error}[/]"
        )
        return
