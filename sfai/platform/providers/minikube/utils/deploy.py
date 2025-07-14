import subprocess
import os
from pathlib import Path
from typing import Any
from sfai.platform.providers.minikube.utils.checks import (
    check_deployment_exists,
    get_app_version,
    _is_minikube_running,
    _start_minikube,
)
from sfai.context.manager import ContextManager
from rich.console import Console
from sfai.constants import (
    ERROR_EMOJI,
    SUCCESS_EMOJI,
    UPDATE_EMOJI,
    PACKAGE_EMOJI,
    DOCKER_EMOJI,
    TEMPLATE_EMOJI,
    WARNING_EMOJI,
    CONFIG_EMOJI,
    CHARTS_PATH,
)

console = Console()
ctx_mgr = ContextManager()


def deploy_to_minikube(path: str = ".", **kwargs: Any) -> None:
    """
    Deploy an application to local Minikube environment.

    Args:
        app_path: Union[str, Path]
            Path to the application directory
        values_path: Optional[str]
            Path to custom Helm values file
        set_values: Optional[str]
            Additional values to set for Helm

    Returns:
        None
    """
    ctx = ctx_mgr.read_context()
    app_path = Path(path).resolve()
    app_name = ctx.get("app_name")
    image_name = app_name or ctx.get("image")
    values_path = kwargs.get("values_path")
    set_values = kwargs.get("set_values")

    # Get app version from version.json
    try:
        image_tag = get_app_version(app_path)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"{ERROR_EMOJI} {e!s}")
        return

    port = 8080

    # Check if deployment with this tag already exists
    if check_deployment_exists(app_name, image_tag):
        raise RuntimeError(
            f"Deployment with tag '{image_tag}' already exists. "
            f"Please update version in version.json to deploy a new version."
        )

    console.print(f"{CONFIG_EMOJI} Checking Minikube status...")
    if not _is_minikube_running():
        if not _start_minikube():
            raise RuntimeError("Minikube is not running and could not be started.")
        # Set kubectl context to minikube after starting
        try:
            console.print(f"{UPDATE_EMOJI} Setting kubectl context to minikube...")
            subprocess.run(["kubectl", "config", "use-context", "minikube"], check=True)
            console.print(f"{SUCCESS_EMOJI} kubectl context set to minikube")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to set kubectl context: {e}") from e
    else:
        # Ensure kubectl is using minikube context even if already running
        try:
            console.print(
                f"{UPDATE_EMOJI} Ensuring kubectl is using minikube context..."
            )
            current_context = subprocess.check_output(
                ["kubectl", "config", "current-context"], text=True
            ).strip()
            if current_context != "minikube":
                console.print(
                    f"Current context is {current_context}, switching to minikube..."
                )
                subprocess.run(
                    ["kubectl", "config", "use-context", "minikube"], check=True
                )
            console.print(f"{SUCCESS_EMOJI} kubectl context is set to minikube")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to check/set kubectl context: {e}") from e

    console.print(f"{CONFIG_EMOJI} Switching to Minikube Docker environment...")
    try:
        # Get Minikube Docker environment variables
        result = subprocess.run(
            ["minikube", "docker-env"], capture_output=True, text=True, check=True
        )
        for line in result.stdout.splitlines():
            if line.startswith("export"):
                key, value = line.replace("export ", "").split("=", 1)
                os.environ[key] = value.strip('"')
        console.print(f"{SUCCESS_EMOJI} Switched to Minikube Docker environment")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Failed to switch to Minikube Docker environment: {e}"
        ) from e

    dockerfile_path = app_path / "Dockerfile"
    if not dockerfile_path.exists():
        console.print(
            f"{ERROR_EMOJI} Dockerfile not found in {app_path}. "
            f"Run `sfai init` or check your app structure."
        )
        return

    console.print(f"{DOCKER_EMOJI} Building Docker image: {image_name}")
    try:
        subprocess.run(
            ["docker", "build", "--no-cache", "-t", f"{image_name}:{image_tag}", "."],
            cwd=app_path,
            check=True,
        )
    except subprocess.CalledProcessError:
        raise RuntimeError(f"{ERROR_EMOJI} Docker build failed.") from None

    chart_path = Path("./helm-chart") if Path("./helm-chart").exists() else CHARTS_PATH
    values_file = chart_path / "values.yaml"
    if not values_file.exists():
        raise RuntimeError(f"{ERROR_EMOJI} values.yaml not found at {values_file}")

    # Save context for future reference
    ctx_mgr.update_platform(
        platform="local",
        values={"image": image_name, "image_tag": image_tag, "port": port},
    )
    # Prepare Helm command with proper arguments
    helm_args = [
        "helm",
        "upgrade",
        "--install",
        app_name,
        str(chart_path),
        "--set",
        f"image.repository={image_name}",
        "--set",
        f"image.tag={image_tag}",
        "--set",
        "image.pullPolicy=Never",
    ]

    # Add custom values file if provided
    if values_path:
        helm_args.extend(["-f", values_path])

    # Add set values if provided
    if set_values:
        for value_pair in set_values.split(","):
            helm_args.extend(["--set", value_pair])

    console.print(f"{PACKAGE_EMOJI} Deploying Helm chart to Minikube...")
    try:
        subprocess.run(helm_args, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"{ERROR_EMOJI} Helm deployment failed: {e}") from e

    console.print(
        f"{SUCCESS_EMOJI} Deployment successful to local Minikube environment"
    )

    # Display service information
    try:
        console.print(f"{TEMPLATE_EMOJI} Service information:")
        subprocess.run(["kubectl", "get", "service", f"{app_name}-service"], check=True)

    except subprocess.CalledProcessError as e:
        console.print(f"{WARNING_EMOJI} Could not retrieve service information: {e}")
