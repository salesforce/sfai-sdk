from typing import Dict, Any, Optional
import subprocess
from pathlib import Path
from sfai.core.base import BasePlatform
from sfai.core.decorators import with_context
from sfai.platform.providers.local.utils import find_free_port
from sfai.core.response_models import BaseResponse
from sfai.context.manager import ContextManager
from rich.console import Console
from sfai.constants import (
    DOCKER_EMOJI,
    SUCCESS_EMOJI,
    WEB_EMOJI,
    SEARCH_EMOJI,
    WARNING_EMOJI,
)

console = Console()
ctx_mgr = ContextManager()


class LocalPlatform(BasePlatform):
    def __init__(self):
        pass

    def init(self, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        pass

    @with_context
    def deploy(self, context: Dict[str, Any], path: Path, **kwargs) -> Dict[str, Any]:
        """Deploy the application to local Docker."""
        try:
            ctx = ctx_mgr.read_context()
            app_name = ctx.get("app_name")
            app_path = Path(path).resolve()

            # Clean up any existing container first
            console.print(f"{DOCKER_EMOJI} Cleaning up existing container: {app_name}")
            self.delete(context)

            # Check if Dockerfile exists
            dockerfile_path = app_path / "Dockerfile"
            if not dockerfile_path.exists():
                raise RuntimeError(f"Dockerfile not found in {app_path}")

            # Build image
            console.print(f"{DOCKER_EMOJI} Building Docker image: {app_name}")
            subprocess.run(
                ["docker", "build", "-t", app_name, "."], cwd=app_path, check=True
            )

            # Find a free local port starting from 8080
            free_port = find_free_port(8080, 8100)

            # Run container
            console.print(f"{DOCKER_EMOJI} Starting container: {app_name}")
            subprocess.run(
                [
                    "docker",
                    "run",
                    "-d",
                    "--name",
                    app_name,
                    "-p",
                    f"{free_port}:8080",
                    "-e",
                    "PORT=8080",
                    app_name,
                ],
                check=True,
            )

            ctx_mgr.update_platform(
                platform="local",
                values={
                    "public_url": f"http://localhost:{free_port}",
                    "port": free_port,
                },
            )

            console.print(f"{SUCCESS_EMOJI} App deployed successfully!")
            console.print(f"{WEB_EMOJI} Available at: http://localhost:{free_port}")

            return BaseResponse(success=True, message="Deployment successful")
        except Exception as e:
            return BaseResponse(
                success=False, error=str(e), message="Deployment failed"
            )

    def delete(self, context: Dict[str, Any]) -> BaseResponse:
        """Stop and remove the Docker container."""
        try:
            ctx = ctx_mgr.read_context()
            app_name = ctx.get("app_name")

            subprocess.run(["docker", "stop", app_name], check=False)
            subprocess.run(["docker", "rm", app_name], check=False)
            console.print(f"{SUCCESS_EMOJI} Container {app_name} stopped and removed")

            return BaseResponse(success=True, message="Container removed")
        except Exception as e:
            return BaseResponse(success=False, error=str(e))

    def logs(self, context: Dict[str, Any]) -> BaseResponse:
        """Get Docker container logs."""
        try:
            ctx = ctx_mgr.read_context()
            app_name = ctx.get("app_name")

            if not app_name:
                return BaseResponse(success=False, error="No app name found")

            result = subprocess.run(
                ["docker", "logs", app_name], capture_output=True, text=True, check=True
            )
            console.print(f"{SEARCH_EMOJI} Logs for {app_name}:")
            console.print(result.stdout)

            return BaseResponse(success=True, message="Logs retrieved")
        except Exception as e:
            return BaseResponse(success=False, error=str(e))

    def open(
        self, context: Dict[str, Any], path: str, url: Optional[str] = None
    ) -> BaseResponse:
        """Open the application in browser."""
        try:
            ctx = ctx_mgr.read_context()
            port = ctx.get("port")
            target_url = url or f"http://localhost:{port}{path}"
            console.print(f"{WEB_EMOJI} Opening {target_url}")
            return BaseResponse(
                success=True, message="Opened in browser", url=target_url
            )
        except Exception as e:
            return BaseResponse(success=False, error=str(e))

    def status(self, context: Dict[str, Any]) -> BaseResponse:
        """Check Docker container status."""
        try:
            ctx = ctx_mgr.read_context()
            app_name = ctx.get("app_name")

            if not app_name:
                return BaseResponse(success=False, error="No app name found")

            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={app_name}"],
                capture_output=True,
                text=True,
                check=True,
            )

            if app_name in result.stdout:
                console.print(f"{SUCCESS_EMOJI} Container {app_name} is running")
                return BaseResponse(success=True, message="Container is running")
            else:
                console.print(f"{WARNING_EMOJI} Container {app_name} is not running")
                return BaseResponse(success=True, message="Container is stopped")
        except Exception as e:
            return BaseResponse(success=False, error=str(e))
