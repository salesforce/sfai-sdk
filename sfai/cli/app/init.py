from __future__ import annotations

import typer
from rich.console import Console
from sfai.app.init import init
from sfai.constants import (
    SUCCESS_EMOJI,
    WARNING_EMOJI,
    WARNING_COLOR,
    APP_NAME_EMOJI,
    TEMPLATE_EMOJI,
    ROCKET_EMOJI,
    LIGHT_BULB_EMOJI,
)

console = Console()

app = typer.Typer(help="Initialize your app")


@app.callback(invoke_without_command=True, help="Initialize your app")
def init_cmd(
    force: bool = typer.Option(False, "--force", help="Force initialize"),
    template: str = typer.Option(
        "fastapi_hello",
        "--template",
        help="Template to use (eg: fastapi_hello or flask_hello)",
    ),
) -> None:
    """
    Initialize a new SFAI application in the current directory.

    Args:
        force: bool
            Whether to force initialization if app is already initialized
        template: str
            Template to use for scaffolding the app (eg: fastapi_hello or flask_hello)

    Returns:
        None
    """
    # Call the Python API function
    result = init(template=template, force=force)

    if not result.success:
        console.print(
            f"{WARNING_EMOJI} [{WARNING_COLOR}] App {result.app_name} "
            f"already initialized use --force to reinitialize[/]"
        )
        return

    app_name = result.app_name

    console.print(f"{SUCCESS_EMOJI} App initialized!")
    console.print(f"{APP_NAME_EMOJI} App name: {app_name}")
    console.print(f"{TEMPLATE_EMOJI} Template: {template}")

    console.print(
        f"\n{ROCKET_EMOJI} Next: Run `[cyan]sfai app deploy[/]` to build "
        f"and deploy your app.\n"
        f" Run `[cyan]sfai platform init[/]` to initialize a cloud "
        f"environment(heroku, aws).\n"
        f"{LIGHT_BULB_EMOJI} Tip: Run `[cyan]sfai app open[/]` to access "
        f"your app locally."
    )
