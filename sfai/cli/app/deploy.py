import typer
from typing import Optional
from rich.console import Console
from sfai.constants import (
    ROCKET_EMOJI,
    CELEBRATE_EMOJI,
    ERROR_EMOJI,
    ERROR_COLOR,
)
from sfai.app.deploy import deploy

console = Console()

app = typer.Typer(help="Deploy an application to the configured environment.")


@app.callback(
    invoke_without_command=True,
    help="Deploy an application to the configured environment.",
)
def deploy_cmd(
    # common options
    platform: Optional[str] = typer.Option(None, help="Platform to deploy to"),
    environment: str = typer.Option("default", help="Environment to deploy to"),
    path: str = typer.Option(
        ".", help="Path to the app folder (default: current directory)"
    ),
    # k8s options
    values_path: Optional[str] = typer.Option(None, help="Path to Helm values file"),
    set_values: Optional[str] = typer.Option(
        None, help="Additional values to set for Helm"
    ),
    # heroku options
    commit_message: Optional[str] = typer.Option(None, help="Commit message"),
    branch: Optional[str] = typer.Option(None, help="Branch name"),
) -> None:
    """
    Deploy the current application to the specified environment.

    Args:
        platform: Optional[str]
            Platform to deploy to
        environment: str
            Environment to deploy to (defaults to "default")
        path: str
            Path to the app folder
        values_path: Optional[str]
            Path to Helm values file
        set_values: Optional[str]
            Additional values to set for Helm
        commit_message: Optional[str]
            Commit message
        branch: Optional[str]
            Branch name
    Returns:
        None
    """

    console.print(f"{ROCKET_EMOJI} Deploying application...")

    result = deploy(
        platform=platform,
        environment=environment,
        path=path,
        values_path=values_path,
        set_values=set_values,
        commit_message=commit_message,
        branch=branch,
    )

    if result.success:
        console.print(f"{CELEBRATE_EMOJI} {result.message}")
    else:
        console.print(f"{ERROR_EMOJI} [{ERROR_COLOR}]{result.error}[/]")
