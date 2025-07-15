import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from sfai.config.view import view
from sfai.config.utils.validate import _get_service_schema
from sfai.constants import ERROR_EMOJI, ERROR_COLOR

app = typer.Typer(help="View service profile details")
console = Console()


@app.callback(invoke_without_command=True)
def view_cmd(
    service: str = typer.Option(..., help="Service name"),
    profile_name: Optional[str] = typer.Option("default", help="Profile to view"),
):
    """View details of a service profile

    Args:
        service: str
            Service name
        profile_name: Optional[str]
            Profile to view
    """

    # Get schema to validate service
    schema = _get_service_schema(service)
    if not schema:
        console.print(f"{ERROR_EMOJI} [{ERROR_COLOR}]Invalid service: {service}[/]")
        return

    # View the profile
    result = view(service, profile_name)

    if not result.success:
        console.print(f"{ERROR_EMOJI} [{ERROR_COLOR}]{result.error}[/]")
        return

    # Display profile information in a table
    table = Table(title=f"{service.capitalize()} Profile: {profile_name}")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")

    profile = result.data
    for key, value in profile.items():
        table.add_row(key, str(value))

    console.print(table)
