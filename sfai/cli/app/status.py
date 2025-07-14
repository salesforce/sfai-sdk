import typer
from typing import Optional
from rich.console import Console
from sfai.constants import ERROR_EMOJI, ERROR_COLOR, SUCCESS_EMOJI, LIGHT_BULB_EMOJI
from sfai.app.status import status
from sfai.platform.switch import switch

app = typer.Typer(help="Show the status of the current app")
console = Console()


@app.callback(invoke_without_command=True, help="Show status of the current app")
def status_cmd(
    platform: Optional[str] = typer.Option(None, help="Platform to show status from"),
) -> None:
    """
    Show the status of the current app from context.
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
    result = status()
    if not result.success:
        console.print(f"{ERROR_EMOJI} [{ERROR_COLOR}]{result.error}[/]")
        return
