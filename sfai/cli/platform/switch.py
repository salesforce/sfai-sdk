from rich.console import Console
from sfai.platform.switch import switch
import typer
from sfai.constants import ERROR_EMOJI, SUCCESS_EMOJI, LIGHT_BULB_EMOJI

app = typer.Typer(help="Switch between different configurations")
console = Console()


@app.command(help="Switch between different configurations")
def switch_platform_cmd(
    platform: str = typer.Argument(
        ..., help="Platform to switch to (local, aws, gcp, heroku)"
    ),
) -> None:
    """
    Switch to a different platform.

    Args:
        platform: str
            Platform to switch to (local, aws, gcp, heroku)

    Returns:
        None
    """
    result = switch(platform)
    if result.success:
        console.print(f"{SUCCESS_EMOJI} Switched to {platform} platform")
    else:
        console.print(f"{ERROR_EMOJI} Platform '{platform}' is not initialized yet.")
        console.print(f"{LIGHT_BULB_EMOJI} Run: sfai platform init {platform}")
