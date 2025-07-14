import typer
from typing import Optional
from rich.console import Console
from sfai.constants import ERROR_EMOJI, ERROR_COLOR, SUCCESS_EMOJI, LIGHT_BULB_EMOJI
from sfai.app.logs import logs
from sfai.platform.switch import switch

console = Console()

app = typer.Typer(help="Show logs for the current app")


@app.callback(invoke_without_command=True, help="Show logs for the current app")
def logs_cmd(
    platform: Optional[str] = typer.Option(None, help="Platform to show logs from"),
) -> None:
    """
    Show logs for the current app.
    """
    if platform:
        result = switch(platform)
        if result.success:
            console.print(f"{SUCCESS_EMOJI} Using {platform} platform")
        else:
            console.print(
                f"{ERROR_EMOJI} Platform '{platform}' is not initialized yet."
            )
            console.print(f"{LIGHT_BULB_EMOJI} Run: sfai platform init {platform}")
            return
    result = logs()
    if not result.success:
        console.print(
            f"{ERROR_EMOJI} [{ERROR_COLOR}] unable to fetch logs: {result.error}[/]"
        )
        return
