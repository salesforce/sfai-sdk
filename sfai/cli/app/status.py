import typer
from typing import Optional
from rich.console import Console
from sfai.constants import ERROR_EMOJI, ERROR_COLOR
from sfai.app.status import status

app = typer.Typer(help="Show the status of the current app")
console = Console()


@app.callback(invoke_without_command=True, help="Show status of the current app")
def status_cmd(
    platform: Optional[str] = typer.Option(None, help="Platform to show status from"),
    environment: Optional[str] = typer.Option(
        None, help="Environment to show status from"
    ),
) -> None:
    """
    Show the status of the current app from context.

    Args:
        platform: Optional[str]
            Platform to show status from
        environment: str
            Environment to show status from (defaults to "default")
    """

    result = status(platform=platform, environment=environment)
    if not result.success:
        console.print(f"{ERROR_EMOJI} [{ERROR_COLOR}]{result.error}[/]")
        return
