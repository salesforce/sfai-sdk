import typer
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt
from sfai.config.update import update
from sfai.config.utils.validate import profile_exists, _get_service_schema
from sfai.constants import (
    SUCCESS_EMOJI,
    ERROR_EMOJI,
    UPDATE_EMOJI,
    SUCCESS_COLOR,
    ERROR_COLOR,
)

app = typer.Typer(help="Update specific values in an existing service profile")
console = Console()


@app.callback(invoke_without_command=True)
def update_cmd(
    service: str = typer.Option(..., help="Service name"),
    profile_name: Optional[str] = typer.Option("default", help="Profile to update"),
    interactive: bool = typer.Option(False, "--interactive", "-i"),
    # full list of possible fields
    org_id: Optional[str] = None,
    environment_id: Optional[str] = None,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
):
    """Update specific values in an existing service profile

    Args:
        service: str
            Service name
        profile_name: Optional[str]
            Profile to update
        interactive: bool
            Run in interactive mode
        org_id: Optional[str]
            MuleSoft organization ID
        environment_id: Optional[str]
            MuleSoft environment ID
        client_id: Optional[str]
            MuleSoft client ID
        client_secret: Optional[str]
            MuleSoft client secret
    """
    schema = _get_service_schema(service)
    if not schema:
        console.print(f"{ERROR_EMOJI} [{ERROR_COLOR}]Invalid service: {service}[/]")
        return

    # Check if profile exists BEFORE prompting for updates
    exists, error = profile_exists(service, profile_name)
    if not exists:
        console.print(f"{ERROR_EMOJI} [{ERROR_COLOR}]{error}[/]")
        return

    schema_keys = set(schema.keys())

    all_cli_args = {
        "org_id": org_id,
        "environment_id": environment_id,
        "client_id": client_id,
        "client_secret": client_secret,
    }

    updates = {}

    if interactive or not any(all_cli_args.get(key) for key in schema_keys):
        # prompt user for each field
        for key, label in schema.items():
            val = Prompt.ask(
                f"{UPDATE_EMOJI} New value for {label} (leave blank to skip)"
            )
            if val:
                updates[key] = val
    else:
        # use only explicitly provided cli args
        for key in schema_keys:
            val = all_cli_args.get(key)
            if val:
                updates[key] = val

    # Don't update if no changes
    if not updates:
        console.print(f"{SUCCESS_EMOJI} No updates provided. Profile unchanged.")
        return

    # Call the API
    result = update(service, updates, profile_name)

    if result.success:
        console.print(
            f"{SUCCESS_EMOJI} Updated [{SUCCESS_COLOR}]{service}[/] profile "
            f"[bold]{profile_name}[/] with new values."
        )
    else:
        console.print(f"{ERROR_EMOJI} [{ERROR_COLOR}]{result.error}[/]")
