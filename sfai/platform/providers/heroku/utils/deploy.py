import json
import subprocess
from pathlib import Path
from typing import Union, Any, Optional
import re
import platform
from sfai.context.manager import ContextManager
from datetime import datetime
from rich.console import Console
from sfai.constants import ROCKET_EMOJI
from sfai.platform.providers.heroku.utils.checks import (
    generate_suffix,
    is_heroku_repo,
    get_default_branch,
)
from sfai.core.response_models import BaseResponse

console = Console()
ctx_mgr = ContextManager()

COLOR_PATTERN = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def _push_with_buildx(app_name: str, app_path: Path) -> None:
    """Build and push a linux/amd64 single-arch image directly with buildx.

    This is used on Apple Silicon machines where the default heroku container:push
    produces multi-arch manifest lists that Heroku's registry doesn't support.

    Args:
        app_name: The Heroku app name (with environment suffix)
        app_path: Path to the application directory
    """

    # Build and push in one step - avoids cross-repo mount optimisation
    subprocess.run(
        [
            "docker",
            "buildx",
            "build",
            "--platform",
            "linux/amd64",
            "--push",  # stream layers directly to prod app repo
            "--no-cache",  # guarantee fresh digests, no mounts
            "--provenance=false",
            "-t",
            f"registry.heroku.com/{app_name}/web",
            ".",
        ],
        check=True,
        cwd=app_path,
    )
    # Release the image
    subprocess.run(
        ["heroku", "container:release", "web", "--app", app_name],
        check=True,
        cwd=app_path,
    )


def create_heroku_app(
    app_name: str,
    base_app_name: str,
    team_name: Optional[str] = None,
    private_space: Optional[str] = None,
    routing: Optional[str] = None,
    deployment_type: Optional[str] = None,
) -> BaseResponse:
    """
    Create a Heroku app with given parameters.

    Args:
        app_name: str
            The name of the Heroku app to create (may include environment suffix)
        base_app_name: str
            The base app name without environment suffix
        team_name: Optional[str]
            The name of the team to create the app in
        private_space: Optional[str]
            The name of the private space to create the app in
        routing: Optional[str]
            The routing type to create the app with
    Returns:
        BaseResponse
            The created app details
    """
    base_name = app_name
    max_attempts = 3
    attempt = 0

    while attempt < max_attempts:
        cmd = ["heroku", "create", app_name, "--json"]
        if team_name:
            cmd.append(f"--team={team_name}")
        if private_space:
            cmd.append(f"--space={private_space}")
        if deployment_type:
            cmd.append(f"--stack={deployment_type}")
        if routing == "internal":
            cmd.append("--internal-routing")

        console.print(
            f"Attempt {attempt + 1} of {max_attempts}: Creating Heroku app "
            f"{app_name}..."
        )

        try:
            result = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # parse JSON response
            app_data = json.loads(COLOR_PATTERN.sub("", result.stdout))
            heroku_config = {
                "app_name": base_app_name,
                "heroku_app_name": app_data.get("name", ""),
                "public_url": app_data.get("web_url", ""),
                "git_url": app_data.get("git_url", ""),
                "team_name": app_data.get("team", ""),
                "private_space": app_data.get("space", ""),
                "deployment_type": app_data.get("build_stack", {}).get("name", ""),
                "routing": (
                    "public"
                    if app_data.get("internal_routing") is None
                    else ("internal" if app_data.get("internal_routing") else "public")
                ),
            }

            return BaseResponse(
                success=True,
                message=f"Initialized with Heroku app {app_name}.",
                data=heroku_config,
            )
        except subprocess.CalledProcessError as e:
            raw_error = e.stderr if hasattr(e, "stderr") else str(e)
            error_message = COLOR_PATTERN.sub("", raw_error)

            # comprehensive checks for name taken errors
            name_taken_indicators = [
                "name is already taken",
                "name is taken",
            ]
            is_name_taken = any(
                indicator in error_message.lower()
                for indicator in name_taken_indicators
            )

            if is_name_taken:
                console.print(
                    f"Name {app_name} is already taken. Generating new name "
                    f"with suffix..."
                )
                attempt += 1
                new_suffix = generate_suffix()
                app_name = f"{base_name}-{new_suffix}"
                console.print(f"trying: {app_name}")
                continue
            else:
                return BaseResponse(
                    success=False,
                    error=error_message,
                )
        except json.JSONDecodeError:
            return BaseResponse(
                success=False,
                error="Failed to parse JSON response from heroku",
            )

    return BaseResponse(
        success=False,
        error=(
            f"Failed to create Heroku app after {max_attempts} attempts "
            f"due to name conflict"
        ),
    )


def deploy_to_heroku(path: Union[str, Path], **kwargs: Any) -> BaseResponse:
    """Deploy the current app to Heroku.

    Args:
        path: The path to the app.
        commit_message: The commit message.
        branch: The branch to deploy to.
    """
    ctx = ctx_mgr.read_context()
    app_path = Path(path).resolve()
    app_name = ctx.get("app_name")
    heroku_app_name = (
        ctx.get("heroku_app_name") or app_name
    )  # fallback to app_name if heroku_app_name not set
    commit_message = kwargs.get("commit_message")
    branch = kwargs.get("branch")
    deployment_type = ctx.get("deployment_type") or "buildpack"

    # Always clear local Heroku-registry images to prevent cross-repo mounts
    try:
        imgs = (
            subprocess.check_output(
                [
                    "docker",
                    "images",
                    "--filter",
                    "reference=registry.heroku.com/*",
                    "--quiet",
                ]
            )
            .decode()
            .strip()
            .splitlines()
        )
        if imgs:
            subprocess.run(["docker", "rmi", "-f", *imgs], check=False)
    except Exception:
        # Non-fatal - continue even if prune fails
        pass

    console.print(
        f"{ROCKET_EMOJI} Deploying {heroku_app_name} to Heroku using "
        f"{deployment_type} deployment type..."
    )

    if deployment_type == "buildpack":
        # check if this is heroku repo
        if not is_heroku_repo(app_path):
            console.print("The current directory is not a Heroku repository.")
            return BaseResponse(
                success=False,
                error="The current directory is not a Heroku repository.",
            )

        # Default commit message if not provided
        if not commit_message:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f"Deploy {app_name} to Heroku at {timestamp}"

        # Get default branch if not provided
        if not branch:
            branch = get_default_branch(app_path)
            console.print(f"Using current branch: {branch}")

        # check if there are any changes to commit
        changes = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=app_path,
            capture_output=True,
            text=True,
            check=False,
        )

        if changes.stdout.strip():
            subprocess.run(["git", "add", "."], cwd=app_path, check=True)
            subprocess.run(
                ["git", "commit", "-m", commit_message], cwd=app_path, check=True
            )
        else:
            console.print("No changes to commit.")

        subprocess.run(["git", "push", "heroku", branch], cwd=app_path, check=True)

        return BaseResponse(
            success=True,
            message="Deployed to Heroku",
        )

    elif deployment_type == "container":
        # Set stack to container
        subprocess.run(
            ["heroku", "stack:set", "container", "--app", heroku_app_name],
            cwd=app_path,
            check=True,
        )
        # login to heroku container registry
        subprocess.run(["heroku", "container:login"], cwd=app_path, check=True)

        # Check if we're on Apple Silicon and use the appropriate method
        if platform.machine() in ["arm64", "aarch64"]:
            console.print(
                "Apple Silicon detected - using environment variables for "
                "Heroku compatibility..."
            )
            _push_with_buildx(heroku_app_name, app_path)
        else:
            # Standard heroku container:push for Intel machines
            subprocess.run(
                ["heroku", "container:push", "web", "--app", heroku_app_name],
                cwd=app_path,
                check=True,
            )
            subprocess.run(
                ["heroku", "container:release", "web", "--app", heroku_app_name],
                cwd=app_path,
                check=True,
            )

        return BaseResponse(
            success=True,
            message="Container deployed successfully",
        )
    else:
        return BaseResponse(
            success=False,
            error=f"Invalid deployment type: {deployment_type}",
        )
