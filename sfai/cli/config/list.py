import typer
from typing import Optional
from rich.console import Console
from sfai.config.list import list
from sfai.constants import ERROR_EMOJI, SUCCESS_COLOR, ERROR_COLOR, WARNING_COLOR

app = typer.Typer(help="Config management")
console = Console()


@app.callback(invoke_without_command=True)
def list_cmd(
    service: Optional[str] = typer.Option(None, help="Filter by specific service name"),
):
    """List service profiles

    Args:
        service: Optional[str]
            Filter by specific service name
    """
    result = list(service)

    if not result.success:
        console.print(f"{ERROR_EMOJI} [{ERROR_COLOR}]{result.error}[/]")
        return

    profiles = result.profiles

    if not profiles:
        console.print(f"[{WARNING_COLOR}]No service profiles found.[/]")
        return

    if service:
        # Single service display
        console.print(f"[{SUCCESS_COLOR}]{service.capitalize()} Profiles[/]:")
        for name in profiles:
            console.print(f"- {name}")
    else:
        # All services display
        for svc, svc_profiles in profiles.items():
            console.print(f"\n[{SUCCESS_COLOR}]{svc.capitalize()} Profiles[/]:")
            for name in svc_profiles:
                console.print(f"- {name}")
