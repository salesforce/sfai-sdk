import typer
from typing import Optional
from rich.console import Console
from sfai.constants import ERROR_EMOJI, ERROR_COLOR, SUCCESS_EMOJI
from sfai.app.delete import delete

app = typer.Typer(help="Delete your application")
console = Console()


@app.callback(invoke_without_command=True, help="Delete the current app")
def delete_cmd(
    platform: Optional[str] = typer.Option(None, help="Platform to delete from"),
    environment: Optional[str] = typer.Option(None, help="Environment to delete from"),
):
    """
    Delete the current app deployment

    Args:
        platform: Optional[str]
            Platform to delete from
        environment: str
            Environment to delete from (defaults to "default")
    """

    result = delete(platform=platform, environment=environment)

    if not result.success:
        console.print(f"{ERROR_EMOJI} [{ERROR_COLOR}]{result.error}[/]")
        raise typer.Exit(code=1)

    name = result.app_name

    console.print(f"{SUCCESS_EMOJI} Deleted app '{name}'...")
