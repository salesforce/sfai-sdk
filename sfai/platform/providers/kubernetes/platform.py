from typing import Dict, Any, Optional
from pathlib import Path
import subprocess
from sfai.core.base import BasePlatform
from sfai.core.decorators import with_context
from sfai.constants import PACKAGE_EMOJI, PORT_EMOJI, ROCKET_EMOJI, CHARTS_PATH
from sfai.core.response_models import BaseResponse
from rich.console import Console
from sfai.platform.providers.kubernetes.utils.helpers import get_app_version
from sfai.platform.providers.kubernetes.utils.checks import (
    _is_kubectl_installed,
    _is_helm_installed,
)

console = Console()


class K8sPlatform(BasePlatform):
    def __init__(self, env: str = "k8s"):
        self.env = env

    @with_context
    def init(self, context: Optional[Dict[str, Any]] = None, **kwargs) -> BaseResponse:
        """
        Initialize Kubernetes platform.

        Args:
            context: Application context
            **kwargs: Additional arguments

        Returns:
            BaseResponse with initialization status
        """
        # Check if kubectl is installed
        if not _is_kubectl_installed():
            return BaseResponse(
                success=False,
                error=(
                    "kubectl not installed. Please install kubectl for "
                    "Kubernetes cluster access."
                ),
            )

        # Check if helm is installed
        if not _is_helm_installed():
            return BaseResponse(
                success=False,
                error=(
                    "Helm not installed. Please install Helm for Kubernetes "
                    "deployments."
                ),
            )

        namespace = kwargs.get("namespace", "default")

        return BaseResponse(
            success=True,
            message=(
                f"Kubernetes platform initialized successfully in namespace {namespace}"
            ),
            namespace=namespace,
        )

    @with_context
    def deploy(self, context: Dict[str, Any], path: Path, **kwargs) -> Dict[str, Any]:
        name = context.get("app_name")
        namespace = context.get("namespace", "default")
        # version path
        version = get_app_version(path)
        context["version"] = version

        # Use local helm-chart folder if it exists, otherwise use default
        chart_path = (
            Path("./helm-chart") if Path("./helm-chart").exists() else CHARTS_PATH
        )

        cmd = [
            "helm",
            "upgrade",
            "--install",
            name,
            str(chart_path),
            "--namespace",
            namespace,
        ]

        # Check if kubectl is installed
        if not _is_kubectl_installed():
            return BaseResponse(
                success=False,
                error=(
                    "kubectl not installed. Please install kubectl for EKS "
                    "cluster access."
                ),
            )

        # Check if helm is installed
        if not _is_helm_installed():
            return BaseResponse(
                success=False,
                error=(
                    "Helm not installed. Please install Helm for Kubernetes "
                    "deployments."
                ),
            )

        # Process set values from kwargs if provided
        set_values = kwargs.get("set_values")
        helm_set = context.get("helm_set", {})
        if set_values:
            for value_pair in set_values.split(","):
                key, value = value_pair.split("=", 1)
                helm_set[key] = value

        # update context with helm_set
        context["helm_set"] = helm_set

        # apply --set values from context ["helm_set"]
        for key, value in helm_set.items():
            cmd.extend(["--set", f"{key}={value}"])

        try:
            subprocess.run(cmd, check=True)
            return BaseResponse(
                success=True,
                message=f"Deployed {name} to {namespace}",
            )
        except subprocess.CalledProcessError as e:
            return BaseResponse(
                success=False,
                error=str(e),
                message="Deployment failed",
            )

    @with_context
    def delete(self, context: Dict[str, Any]) -> Dict[str, Any]:
        name = context.get("app_name")
        namespace = context.get("namespace", "default")
        cmd = ["helm", "uninstall", name, "--namespace", namespace]
        subprocess.run(cmd, check=True)
        return BaseResponse(
            success=True,
            message=f"Deleted {name} from {namespace}",
        )

    @with_context
    def logs(self, context: Dict[str, Any]) -> Dict[str, Any]:
        name = context.get("app_name")
        namespace = context.get("namespace", "default")
        pod = subprocess.run(
            [
                "kubectl",
                "get",
                "pods",
                "-l",
                f"app={name}",
                "-n",
                namespace,
                "-o",
                "jsonpath={.items[0].metadata.name}",
            ],
            check=False,
            capture_output=True,
            text=True,
        ).stdout.strip()

        if not pod:
            return BaseResponse(
                success=False,
                error="No pod found.",
            )
        else:
            subprocess.run(
                ["kubectl", "logs", pod, "-n", namespace],
                check=True,
            )
            return BaseResponse(
                success=True,
                message=f"Logs for {name} from {pod}",
            )

    @with_context
    def open(
        self,
        context: Dict[str, Any],
        path: str,
        port: int = 8080,
        url: Optional[str] = None,
    ) -> Dict[str, Any]:
        name = context.get("app_name")
        cmd = ["kubectl", "port-forward", f"svc/{name}-service", f"{port}:80"]
        subprocess.run(cmd, check=True)
        url = f"http://localhost:{port}{path}"
        return BaseResponse(success=True, message=f"Opened {name} at {url}", url=url)

    @with_context
    def status(self, context: Dict[str, Any]) -> Dict[str, Any]:
        name = context.get("app_name")
        namespace = context.get("namespace", "default")
        cmds = [
            (
                f"{PACKAGE_EMOJI} Pods",
                ["kubectl", "get", "pods", "-l", f"app={name}", "-n", namespace],
            ),
            (
                f"{PORT_EMOJI} Services",
                ["kubectl", "get", "svc", f"{name}-service", "-n", namespace],
            ),
            (
                f"{ROCKET_EMOJI} Deployments",
                ["kubectl", "get", "deployment", name, "-n", namespace],
            ),
        ]
        for title, cmd in cmds:
            console.print(f"{title}:")
            subprocess.run(cmd, check=True)
        return BaseResponse(
            success=True,
            message=f"Status for {name} in {namespace}",
        )
