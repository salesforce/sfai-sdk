import typer
from typing import Optional
from rich.console import Console
from sfai.constants import ERROR_EMOJI, ERROR_COLOR, SUCCESS_EMOJI, LIGHT_BULB_EMOJI
from sfai.app.delete import delete
from sfai.platform.switch import switch

app = typer.Typer(help="Delete your application")
console = Console()


@app.callback(invoke_without_command=True, help="Delete the current app")
def delete_cmd(
    platform: Optional[str] = typer.Option(None, help="Platform to delete from"),
):
    """
    Delete the current app deployment
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
    result = delete()

    if not result.success:
        console.print(f"{ERROR_EMOJI} [{ERROR_COLOR}]{result.error}[/]")
        raise typer.Exit(code=1)

    name = result.app_name

    console.print(f"{SUCCESS_EMOJI} Deleted app '{name}'...")
