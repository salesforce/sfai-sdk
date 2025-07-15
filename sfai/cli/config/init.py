import typer
from rich.console import Console
from rich.prompt import Prompt
from sfai.config.init import init
from sfai.config.utils.validate import _get_schema_fields
from sfai.constants import (
    SUCCESS_EMOJI,
    ERROR_EMOJI,
    WARNING_EMOJI,
    SECURITY_EMOJI,
    SUCCESS_COLOR,
    ERROR_COLOR,
)

app = typer.Typer(help="Initialize configuration")
console = Console()


@app.callback(invoke_without_command=True)
def init_cmd(
    service: str = typer.Option(None, help="service name, e.g. mulesoft, heroku, aws"),
    profile_name: str = typer.Option(
        None, help="profile name to store credentials under"
    ),
    interactive: bool = typer.Option(
        False, "-i", "--interactive", help="Run in interactive mode"
    ),
    # credentials flags
    org_id: str = typer.Option(None, help="MuleSoft organization ID"),
    environment_id: str = typer.Option(None, help="MuleSoft environment ID"),
    client_id: str = typer.Option(None, help="MuleSoft client ID"),
    client_secret: str = typer.Option(None, help="MuleSoft client secret"),
) -> None:
    """
    Configure service connection settings.

    Args:
        service: str
            Name of the service to configure credentials for
        profile_name: str
            Name of the profile to store credentials under
        interactive: bool
            Run in interactive mode
        org_id: str
            MuleSoft organization ID
        environment_id: str
            MuleSoft environment ID
        client_id: str
            MuleSoft client ID
        client_secret: str
            MuleSoft client secret
    Returns:
        None
    """
    # Prompt for service if missing
    if not service:
        service = Prompt.ask(
            "Which service to configure (e.g., mulesoft)", default="mulesoft"
        )

    # Get schema fields and validate service
    schema_fields = _get_schema_fields(service)
    if not schema_fields:
        console.print(
            f"{ERROR_EMOJI} [{ERROR_COLOR}]Invalid or missing service: {service}[/]"
        )
        return

    # Define profile name
    profile_name = profile_name or "default"
    if interactive:
        profile_name = Prompt.ask(
            f"Enter {service} profile name for storing credentials", default="default"
        )

    # all CLI values captured
    all_cli_args = {
        "org_id": org_id,
        "environment_id": environment_id,
        "client_id": client_id,
        "client_secret": client_secret,
    }

    credentials = {}

    # Collect credentials
    if interactive:
        for field_name, description in schema_fields.items():
            val = Prompt.ask(
                f"{SECURITY_EMOJI} {description}",
                password=("secret" in field_name.lower()),
            )
            if not val:
                console.print(
                    f"{ERROR_EMOJI} [{ERROR_COLOR}]Missing required field: "
                    f"{description}[/]"
                )
                return
            credentials[field_name] = val
    else:
        for field_name in schema_fields:
            val = all_cli_args.get(field_name)
            if val is not None:
                credentials[field_name] = val

        if not credentials:
            for field_name, description in schema_fields.items():
                val = Prompt.ask(
                    f"{SECURITY_EMOJI} {description}",
                    password=("secret" in field_name.lower()),
                )
                if not val:
                    console.print(
                        f"{ERROR_EMOJI} [{ERROR_COLOR}]Missing required field: "
                        f"{description}[/]"
                    )
                    return
                credentials[field_name] = val

        # warn if irrelevant keys were passed
        invalid_keys = [
            k
            for k in all_cli_args
            if k not in schema_fields and all_cli_args[k] is not None
        ]
        if invalid_keys:
            console.print(
                f"{WARNING_EMOJI} Ignored keys not part of {service}: "
                f"{', '.join(invalid_keys)}"
            )

    # Use the API function
    result = init(service=service, config=credentials, profile_name=profile_name)

    if result.success:
        console.print(
            f"{SUCCESS_EMOJI} [{SUCCESS_COLOR}]{service.capitalize()}[/] "
            f"credentials saved under profile [bold]{profile_name}[/]."
        )
    else:
        console.print(f"{ERROR_EMOJI} [{ERROR_COLOR}]{result.error}[/]")
