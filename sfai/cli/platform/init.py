import typer
from typing import Optional
from rich.console import Console
from sfai.context.manager import ContextManager
from rich.prompt import Prompt
from sfai.platform.init import init
from sfai.constants import ERROR_EMOJI, SUCCESS_EMOJI, ROCKET_EMOJI

app = typer.Typer(help="Initialize or update cloud/local environment in context")
console = Console()
ctx_mgr = ContextManager()


@app.callback(
    invoke_without_command=True,
    help="Initialize or update cloud/local environment in context",
)
def init_platform_cmd(
    platform: Optional[str] = typer.Option(
        None, help="Platform type (local, eks, gcp, heroku)"
    ),
    environment: str = typer.Option("default", help="Environment name"),
    # heroku options
    app_name: Optional[str] = typer.Option(None, help="Heroku app name (for heroku)"),
    team_name: Optional[str] = typer.Option(None, help="Heroku team name (for heroku)"),
    private_space: Optional[str] = typer.Option(
        None, help="Heroku private space name (for heroku)"
    ),
    deployment_type: Optional[str] = typer.Option(
        None, help="Deployment type (for heroku)"
    ),
    routing: Optional[str] = typer.Option(None, help="Routing type (for heroku)"),
    # eks options
    cluster_name: Optional[str] = typer.Option(None, help="EKS cluster name (for eks)"),
    region: Optional[str] = typer.Option(None, help="AWS region (for eks)"),
    profile: Optional[str] = typer.Option(None, help="AWS profile (for eks)"),
    namespace: Optional[str] = typer.Option(None, help="namespace (for eks)"),
    ecr_repo: Optional[str] = typer.Option(None, help="ECR repository (for eks)"),
    # interactive options
    interactive: bool = typer.Option(
        False, "-i", "--interactive", help="Interactive mode"
    ),
    skip_confirm: bool = typer.Option(
        False, "-y", "--yes", help="Skip confirmation of default values"
    ),
) -> None:
    """
    Initialize or update cloud/local environment in context

    Args:
        platform: str
            Platform type (local, eks, gcp, heroku)
        environment: str
            Environment name (defaults to "default")
        app_name: Optional[str]
            Heroku app name (for heroku)
        team_name: Optional[str]
            Heroku team name (for heroku)
        private_space: Optional[str]
            Heroku private space name (for heroku)
        deployment_type: Optional[str]
            Deployment type (for heroku)
        routing: Optional[str]
            Routing type (for heroku)
        cluster_name: Optional[str]
            EKS cluster name (for eks)
        region: Optional[str]
            AWS region (for eks)
        profile: Optional[str]
            AWS profile (for eks)
        namespace: Optional[str]
            namespace (for eks)
        ecr_repo: Optional[str]
            ECR repository (for eks)
        interactive: bool
            Interactive mode
        skip_confirm: bool
            Skip confirmation of default values
    """
    context = ctx_mgr.read_context()
    if not context:
        console.print(f"{ERROR_EMOJI} No app context found. Run `sfai init app` first.")
        return

    current_env = context.get("active_env", {})

    if not platform:
        platform = Prompt.ask(
            "Enter the platform type",
            choices=["eks", "heroku", "minikube"],
            default=current_env or "local",
        )
    environment = Prompt.ask(
        "Enter the environment",
        default=environment or context.get("environment", "default"),
    )

    if platform == "heroku":
        if interactive:
            app_name = Prompt.ask(
                "Enter the app name",
                default=app_name or context.get("app_name", "").lower(),
            )
            team_name = Prompt.ask(
                "Enter the team name", default=team_name or context.get("team_name", "")
            )
            if team_name:
                private_space = Prompt.ask(
                    "Enter the private space name",
                    default=private_space or context.get("private_space", ""),
                )
            else:
                private_space = ""
            deployment_type = Prompt.ask(
                "Enter the deployment type",
                choices=["container", "buildpack"],
                default=deployment_type or context.get("deployment_type", "buildpack"),
            )
            routing = Prompt.ask(
                "Enter the routing type",
                choices=["internal", "public"],
                default=routing or context.get("routing", "public"),
            )
        else:
            app_name = app_name or context.get("app_name", "").lower()
            team_name = team_name or context.get("team_name", "")
            private_space = private_space or context.get("private_space", "")
            deployment_type = deployment_type or context.get(
                "deployment_type", "buildpack"
            )
            routing = routing or context.get("routing", "public")
            if not skip_confirm:
                console.print(
                    f"Initializing [cyan]{platform}[/] environment with the "
                    f"following values:"
                )
                console.print(f"  App Name: [cyan]{app_name}[/]")
                console.print(f"  Team Name: [cyan]{team_name or ''}[/]")
                console.print(f"  Private Space: [cyan]{private_space or ''}[/]")
                console.print(f"  Deployment Type: [cyan]{deployment_type}[/]")
                console.print(f"  Routing Type: [cyan]{routing}[/]")
                confirm = Prompt.ask(
                    "Are you sure you want to continue?",
                    choices=["y", "n"],
                    default="y",
                )
                if confirm.lower() not in ["y", "yes"]:
                    console.print(
                        f"{ERROR_EMOJI} Environment initialization cancelled."
                    )
                    return

    if platform == "eks":
        if interactive:
            cluster_name = Prompt.ask(
                "Enter the EKS cluster name",
                default=cluster_name or context.get("cluster_name"),
            )
            region = Prompt.ask(
                "Enter the region", default=region or context.get("region", "us-west-2")
            )
            profile = Prompt.ask(
                "Enter the profile",
                default=profile or context.get("profile", "default"),
            )
            namespace = Prompt.ask(
                "Enter the namespace",
                default=namespace or context.get("namespace", "default"),
            )
            ecr_repo = Prompt.ask(
                "Enter the ECR repository",
                default=ecr_repo or context.get("ecr_repo", f"{app_name}"),
            )
        else:
            cluster_name = cluster_name or context.get("cluster_name")
            region = region or context.get("region", "us-east-1")
            profile = profile or context.get("profile", "default")
            namespace = namespace or context.get("namespace", "default")
            ecr_repo = ecr_repo or context.get("ecr_repo", f"{app_name}")
            if not skip_confirm:
                console.print(
                    f"Initializing [cyan]{platform}[/] environment with the "
                    f"following values:"
                )
                console.print(f"  Cluster Name: [cyan]{cluster_name}[/]")
                console.print(f"  Region: [cyan]{region}[/]")
                console.print(f"  Profile: [cyan]{profile}[/]")
                console.print(f"  Namespace: [cyan]{namespace}[/]")
                console.print(f"  ECR Repository: [cyan]{ecr_repo}[/]")
                confirm = Prompt.ask(
                    "Are you sure you want to continue?",
                    choices=["y", "n"],
                    default="y",
                )
                if confirm.lower() not in ["y", "yes"]:
                    console.print(
                        f"{ERROR_EMOJI} Environment initialization cancelled."
                    )
                    return

    result = init(
        platform=platform,
        environment=environment,
        # heroku options
        app_name=app_name,
        team_name=team_name,
        private_space=private_space,
        deployment_type=deployment_type,
        routing=routing,
        # eks options
        cluster_name=cluster_name,
        region=region,
        profile=profile,
        namespace=namespace,
        ecr_repo=ecr_repo,
        # interactive options
        interactive=interactive,
        skip_confirm=skip_confirm,
    )

    if result.success:
        # Get the environment-specific app name from result data if available
        environment_app_name = result.data.get("app_name") if result.data else None
        app_name = environment_app_name or context.get("app_name")
        console.print(
            f"{SUCCESS_EMOJI} {platform} environment initialized → app_name: {app_name}"
        )
        if team_name:
            console.print(f"🔗 Team: {team_name}")
        if private_space:
            console.print(f"🔗 Private Space: {private_space}")
        console.print(
            f"{ROCKET_EMOJI} Next: Run `sfai app deploy` to deploy your app to "
            f"{platform}."
        )
    else:
        console.print(f"{ERROR_EMOJI} {result.error}")
