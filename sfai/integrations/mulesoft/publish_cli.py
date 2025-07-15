import os
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from sfai.context.manager import ContextManager
from sfai.integrations.registry import INTEGRATION_REGISTRY
from sfai.constants import ROCKET_EMOJI

ctx_mgr = ContextManager()

console = Console()


def publish_cli(
    profile: str = typer.Option(None, help="MuleSoft profile"),
    interactive: bool = typer.Option(False, help="Run in interactive mode"),
    name: str = typer.Option(None, help="Asset/API name"),
    version: str = typer.Option(None, help="Asset/API version"),
    oas_file: str = typer.Option(None, help="OpenAPI spec file"),
    description: str = typer.Option(None, help="Description"),
    tags: str = typer.Option(None, help="Tags"),
    implementation_uri: str = typer.Option(None, help="Implementation URI"),
    endpoint_uri: str = typer.Option(None, help="Endpoint URI"),
    endpoint_path: str = typer.Option(None, help="Endpoint path"),
    gateway_id: str = typer.Option(None, help="Gateway ID"),
    gateway_version: str = typer.Option(None, help="Gateway version"),
    skip_confirm: bool = typer.Option(
        False, help="Skip confirmation of default values"
    ),
):
    ctx = ctx_mgr.read_context()
    if not ctx:
        console.print(
            "[bold red]MuleSoft not configured for this app. "
            "Please run `sfai config init --service mulesoft` first to set up "
            "your MuleSoft credentials.[/]"
        )
        return

    mulesoft_config = ctx.get("mulesoft", {})
    asset = mulesoft_config.get("asset", {})
    api = mulesoft_config.get("api", {})
    public_url = ctx.get("public_url", "")
    app_name = ctx.get("app_name", "")
    profile_name = profile or mulesoft_config.get("profile")
    if not profile_name:
        # Try to get the first available profile
        profiles = ctx_mgr.list_service_profiles("mulesoft")
        if profiles:
            profile_name = profiles[0]
        else:
            profile_name = "default"

    profile = ctx_mgr.get_service_profile("mulesoft", profile_name)
    if not profile:
        console.print(
            f"MuleSoft profile {profile_name} not found."
            f"Please run `sfai config init --service mulesoft` to set up a "
            f"profile for this app\n"
        )
        return

    # Collect all inputs
    if interactive:
        name = Prompt.ask("Asset/API name", default=asset.get("name") or app_name)
        profile_name = Prompt.ask("Profile name", default=profile_name)
        if not version:
            if asset.get("version"):
                default_version = asset.get("version")
                try:
                    major, minor, patch = map(int, default_version.split("."))
                    patch += 1
                    incremental_version = f"{major}.{minor}.{patch}"
                    version = Prompt.ask(
                        "Enter the asset version", default=incremental_version
                    )
                except ValueError:
                    # If we can't parse the version, just use it as is
                    version = Prompt.ask(
                        "Enter the asset version", default=default_version
                    )
            else:
                version = Prompt.ask("Enter the asset version", default="1.0.0")
        oas_file = Prompt.ask(
            "OpenAPI spec file", default=asset.get("oas_file", "openapi.yaml")
        )
        description = Prompt.ask("Description", default=asset.get("description", ""))
        tags_input = Prompt.ask("Tags", default="sf-api-catalog, sf-api-topic")
        tags = [t.strip() for t in tags_input.split(",")]

        implementation_uri = Prompt.ask(
            "Implementation URI", default=api.get("implementation_uri") or public_url
        )
        endpoint_uri = Prompt.ask("Endpoint URI", default=api.get("endpoint_uri"))
        endpoint_path = Prompt.ask(
            "Endpoint Path",
            default=api.get("endpoint_path") or name.replace("-", "_").lower(),
        )

        gateway_id = Prompt.ask("Gateway ID", default=api.get("gateway_id"))
        gateway_version = Prompt.ask(
            "Gateway Version", default=api.get("gateway_version")
        )
    else:
        name = app_name or asset.get("name")
        profile_name = profile_name or mulesoft_config.get("profile", "default")
        if not version and asset.get("version"):
            try:
                major, minor, patch = map(int, asset.get("version").split("."))
                patch += 1
                version = f"{major}.{minor}.{patch}"
            except ValueError as e:
                console.print(f"[bold red]Error parsing version: {e}[/]")
        elif not version:
            version = "1.0.0"
        oas_file = asset.get("oas_file", "openapi.yaml")
        description = asset.get("description", "")
        tags = asset.get("tags", ["sf-api-catalog", "sf-api-topic"])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]

        implementation_uri = api.get("implementation_uri") or public_url
        if not implementation_uri:
            implementation_uri = Prompt.ask(
                "Enter the Implementation URI", default=public_url
            )
        endpoint_uri = api.get("endpoint_uri") or endpoint_uri
        if not endpoint_uri:
            endpoint_uri = Prompt.ask(
                "Enter the Endpoint URI", default=api.get("endpoint_uri")
            )
        endpoint_path = name.replace("-", "_").lower() or api.get("endpoint_path")
        gateway_id = api.get("gateway_id") or gateway_id
        if not gateway_id:
            gateway_id = Prompt.ask(
                "Enter the Flex Gateway ID", default=api.get("gateway_id")
            )
        gateway_version = api.get("gateway_version") or gateway_version
        if not gateway_version:
            gateway_version = Prompt.ask(
                "Enter the Flex Gateway Version", default=api.get("gateway_version")
            )

    if not os.path.exists(oas_file):
        console.print(f"[bold red]OpenAPI spec file not found: {oas_file}[/]")
        return

    # Verify the profile exists
    mulesoft_profile = ctx_mgr.get_service_profile("mulesoft", profile_name)
    if not mulesoft_profile:
        console.print(f"[bold red]MuleSoft profile {profile_name} not found.[/]")
        console.print(
            "[yellow]Run `sfai connect mulesoft` to configure MuleSoft credentials.[/]"
        )
        return

    if not skip_confirm:
        # Show full summary
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_row("Name", f"[cyan]{name}[/]")
        table.add_row("Version", f"[cyan]{version}[/]")
        table.add_row("OpenAPI", f"[cyan]{oas_file}[/]")
        table.add_row("Description", f"[cyan]{description}[/]")
        table.add_row("Tags", f"[cyan]{tags}[/]")
        table.add_row(
            "Implementation URI",
            f"[cyan][link={implementation_uri}]{implementation_uri}[/]",
        )
        table.add_row("Endpoint URI", f"[cyan][link={endpoint_uri}]{endpoint_uri}[/]")
        table.add_row("Endpoint Path", f"[cyan]{endpoint_path}[/]")
        table.add_row("Gateway ID", f"[cyan]{gateway_id}[/]")
        table.add_row("Gateway Version", f"[cyan]{gateway_version}[/]")
        table.add_row("Profile", f"[cyan]{profile_name}[/]")

        # === Render Panel ===
        console.print(
            Panel.fit(
                table,
                title="[bold blue]Review all details before proceeding",
                border_style="blue",
            )
        )

        # === Steps Section ===
        console.print("\n[bold blue]Steps to be executed:[/]")
        console.print("[green]✓[/] [cyan]Publish asset to Exchange[/]")
        console.print("[green]✓[/] [cyan]Create API in API Manager[/]")
        console.print("[green]✓[/] [cyan]Deploy API to FlexGateway[/]")

        confirm = Prompt.ask(
            "\nProceed with publishing and deployment?", default="y", choices=["y", "n"]
        )
        if confirm.lower() != "y":
            console.print("[yellow]Operation cancelled.[/]")
            return

    # publish asset
    publish_result = INTEGRATION_REGISTRY["mulesoft"].publish(
        ctx=ctx,
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
        profile=profile_name,
    )
    if not publish_result.success:
        console.print(f"[bold red]Error publishing asset: {publish_result.error}[/]")
        return
    else:
        console.print("[bold green]Asset published successfully.[/]")

    if endpoint_uri and endpoint_path:
        # Clean up endpoint URI to ensure it doesn't end with a slash
        if endpoint_uri.endswith("/"):
            endpoint_uri = endpoint_uri[:-1]

        # Ensure endpoint path starts with a slash
        if not endpoint_path.startswith("/"):
            endpoint_path = f"/{endpoint_path}"

        # Display access URL
        access_url = f"{endpoint_uri}{endpoint_path}/"
        console.print(f"\n{ROCKET_EMOJI} Your API is now accessible at:")
        console.print(f"[bold cyan]{access_url}[/]")
    else:
        console.print(
            "\n[yellow]Note: Complete endpoint information not available. "
            "Access URL could not be generated.[/]"
        )
        if not endpoint_uri:
            console.print("[yellow]Missing endpoint URI in configuration.[/]")
        if not endpoint_path:
            console.print("[yellow]Missing endpoint path in configuration.[/]")

    console.print(
        "\n[bold green]✓ MuleSoft asset published, API created, and "
        "deployed successfully![/]"
    )
