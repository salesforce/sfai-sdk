import json
import subprocess
import os
from pathlib import Path
from rich.console import Console
from sfai.constants import ERROR_EMOJI, SUCCESS_EMOJI, ROCKET_EMOJI

console = Console()


def _is_minikube_installed() -> bool:
    """Check if minikube is installed."""
    try:
        subprocess.run(["minikube", "version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _is_minikube_running() -> bool:
    """
    Check if Minikube is currently running.

    Args:
        None

    Returns:
        bool
            True if Minikube is running, False otherwise
    """
    try:
        result = subprocess.run(
            ["minikube", "status"], capture_output=True, text=True, check=True
        )
        return "Running" in result.stdout
    except subprocess.CalledProcessError:
        return False


def _start_minikube() -> bool:
    """
    Start Minikube if it's not already running.

    Args:
        None

    Returns:
        bool
            True if Minikube started successfully, False otherwise
    """
    try:
        console.print(f"{ROCKET_EMOJI} Starting Minikube...")
        subprocess.run(["minikube", "start"], check=True)
        console.print(f"{SUCCESS_EMOJI} Minikube started successfully.")
    except subprocess.CalledProcessError:
        console.print(f"{ERROR_EMOJI} Failed to start Minikube.")
        return False
    return True


def _use_minikube_docker() -> bool:
    """
    Configure environment to use Minikube's Docker daemon.

    Args:
        None

    Returns:
        bool
            True if successful, False otherwise
    """
    try:
        result = subprocess.run(
            ["minikube", "docker-env"], capture_output=True, text=True, check=True
        )
        for line in result.stdout.splitlines():
            if line.startswith("export"):
                key, value = line.replace("export ", "").split("=", 1)
                os.environ[key] = value.strip('"')
        return True
    except Exception:
        return False


def get_app_version(app_path: Path) -> str:
    """
    Get application version from version.json file.

    Args:
        app_path: Path to the application directory

    Returns:
        The version string

    Raises:
        FileNotFoundError: If version.json file is not found
        ValueError: If version.json exists but doesn't contain a version field
    """
    app_path = Path(app_path) if isinstance(app_path, str) else app_path
    version_file = app_path / "version.json"
    if not version_file.exists():
        raise FileNotFoundError(
            f"version.json not found in {app_path}. Please create a "
            f"version.json file with a 'version' field."
        )

    try:
        with open(version_file, "r") as f:
            version_data = json.load(f)
            if "version" in version_data:
                return version_data["version"]
            raise ValueError(
                "version.json found but missing 'version' field. Please add "
                "a 'version' field."
            )
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in version.json: {e!s}") from e


def check_deployment_exists(app_name: str, image_tag: str) -> bool:
    """
    Check if a deployment with the given app name and image tag already exists.

    Args:
        app_name: Name of the application
        image_tag: Image tag to check

    Returns:
        True if deployment exists with this tag, False otherwise
    """
    try:
        result = subprocess.run(
            [
                "kubectl",
                "get",
                "deployment",
                app_name,
                "-o",
                "jsonpath={.spec.template.spec.containers[0].image}",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        existing_image = result.stdout.strip()
        return existing_image and f":{image_tag}" in existing_image
    except Exception:
        # Assume it doesn't exist if command fails
        return False


def get_public_url(app_name: str, namespace: str) -> str:
    try:
        cmd = [
            "kubectl",
            "get",
            "ingress",
            f"{app_name}-ingress",
            "-n",
            namespace,
            "-o",
            "json",
        ]
        output = subprocess.check_output(cmd, text=True)
        ingress = json.loads(output)

        alb_hostname = ingress["status"]["loadBalancer"]["ingress"][0]["hostname"]
        return f"http://{alb_hostname}/"
    except Exception as e:
        return f"Could not determine ALB URL: {e}"
