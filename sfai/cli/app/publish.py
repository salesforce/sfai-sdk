import typer
from typing import Optional, List
from rich.console import Console
from sfai.integrations.mulesoft.publish_cli import publish_cli

app = typer.Typer(help="Publish assets and APIs to MuleSoft")
console = Console()


@app.callback(invoke_without_command=True, help="Publish assets and APIs to MuleSoft")
def publish_cmd(
    service: str = typer.Option("mulesoft", help="Service to publish to"),
    name: Optional[str] = typer.Option(None, help="Asset/API name"),
    version: Optional[str] = typer.Option(None, help="Version"),
    oas_file: Optional[str] = typer.Option(None, help="OpenAPI spec file"),
    description: Optional[str] = typer.Option(None, help="Description"),
    tags: Optional[List[str]] = typer.Option(None, help="Tags"),
    implementation_uri: Optional[str] = typer.Option(None, help="Implementation URI"),
    endpoint_uri: Optional[str] = typer.Option(None, help="Endpoint URI"),
    endpoint_path: Optional[str] = typer.Option(None, help="Endpoint Path"),
    gateway_id: Optional[str] = typer.Option(None, help="Gateway ID"),
    gateway_version: Optional[str] = typer.Option(None, help="Gateway Version"),
    profile: Optional[str] = typer.Option(None, help="MuleSoft profile"),
    interactive: bool = typer.Option(
        False, "-i", "--interactive", help="Run in interactive mode"
    ),
    skip_confirm: bool = typer.Option(
        False, "-y", "--yes", help="Skip confirmation of default values"
    ),
) -> None:
    if not service:
        console.print(
            "[bold red]No service specified. Please run "
            "`sfai publish --help` for more information.[/]"
        )
        return

    if service == "mulesoft":
        publish_cli(
            profile=profile,
            name=name,
            version=version,
            oas_file=oas_file,
            description=description,
            tags=tags,
            implementation_uri=implementation_uri,
            endpoint_uri=endpoint_uri,
            endpoint_path=endpoint_path,
            gateway_id=gateway_id,
            gateway_version=gateway_version,
            interactive=interactive,
            skip_confirm=skip_confirm,
        )
