import typer
from rich.console import Console
from sfai.app.context import get_context, delete_context
from sfai.ui.context_display import display_context
from sfai.constants import ERROR_EMOJI, SUCCESS_EMOJI

console = Console()

app = typer.Typer(help="Manage application context")


@app.callback(invoke_without_command=True, help="Show the current app context")
def handle_context_cmd(
    delete: bool = typer.Option(
        False, "--delete", help="Delete the current app context"
    ),
):
    result = get_context()
    if delete:
        delete_result = delete_context()
        if delete_result.success:
            console.print(
                f"{SUCCESS_EMOJI} Context for {delete_result.app_name} deleted"
            )
        else:
            console.print(f"{ERROR_EMOJI} {delete_result.message}")
    if not result.success:
        console.print(f"{ERROR_EMOJI} {result.error}")
    else:
        display_context(result.context)
