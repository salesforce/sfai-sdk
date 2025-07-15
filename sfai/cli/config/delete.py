import typer
from typing import Optional
from rich.console import Console
from rich.prompt import Confirm
from sfai.config.delete import delete
from sfai.config.utils.validate import _get_service_schema
from sfai.constants import (
    SUCCESS_EMOJI,
    ERROR_EMOJI,
    QUESTION_EMOJI,
    SUCCESS_COLOR,
    ERROR_COLOR,
)

app = typer.Typer(help="Delete service profiles")
console = Console()


@app.callback(invoke_without_command=True)
def delete_cmd(
    service: str = typer.Option(..., help="Service name"),
    profile_name: Optional[str] = typer.Option("default", help="Profile to delete"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Delete without confirmation"
    ),
):
    """Delete a service profile

    Args:
        service: str
            Service name
        profile_name: Optional[str]
            Profile to delete
        force: bool
            Delete without confirmation

    Returns:
        None
    """

    # Get schema to validate service
    schema = _get_service_schema(service)
    if not schema:
        console.print(f"{ERROR_EMOJI} [{ERROR_COLOR}]Invalid service: {service}[/]")
        return

    # Ask for confirmation unless force is specified
    if not force:
        confirmed = Confirm.ask(
            f"{QUESTION_EMOJI} Are you sure you want to delete the profile "
            f"'{profile_name}' for service '{service}'?",
            default=False,
        )
        if not confirmed:
            console.print("Operation cancelled.")
            return

    # Delete the profile
    result = delete(service, profile_name)

    if result.success:
        console.print(f"{SUCCESS_EMOJI} [{SUCCESS_COLOR}]{result.message}[/]")
    else:
        console.print(f"{ERROR_EMOJI} [{ERROR_COLOR}]{result.error}[/]")
