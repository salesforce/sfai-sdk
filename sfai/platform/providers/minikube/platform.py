from typing import Dict, Any, Optional
from sfai.core.base import BasePlatform
from sfai.platform.providers.kubernetes.platform import K8sPlatform
from sfai.core.decorators import with_context
from sfai.core.response_models import BaseResponse
from sfai.platform.providers.minikube.utils.deploy import deploy_to_minikube
from sfai.platform.providers.minikube.utils.checks import (
    _is_minikube_running,
    _start_minikube,
    _is_minikube_installed,
)
from sfai.platform.providers.kubernetes.utils.checks import (
    _is_kubectl_installed,
    _is_helm_installed,
)
from sfai.context.manager import ContextManager
from pathlib import Path
import subprocess

ctx_mgr = ContextManager()


class MinikubePlatform(BasePlatform):
    def __init__(self):
        self.k8s = K8sPlatform(env="minikube")

    def init(self, context: Dict[str, Any], **kwargs) -> BaseResponse:
        """
        Initialize the minikube platform.

        Args:
            context: Application context
            **kwargs: Additional arguments

        Returns:
            BaseResponse with initialization status
        """
        # Check if minikube is installed
        if not _is_minikube_installed():
            return BaseResponse(
                success=False,
                error=(
                    "Minikube not installed. Please install minikube for "
                    "local Kubernetes development."
                ),
            )

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

        # Check if minikube is running, start if needed
        if not _is_minikube_running():
            if not _start_minikube():
                return BaseResponse(
                    success=False,
                    error="Minikube is not running and could not be started.",
                )

        # Set kubectl context to minikube
        try:
            subprocess.run(["kubectl", "config", "use-context", "minikube"], check=True)
        except subprocess.CalledProcessError as e:
            return BaseResponse(
                success=False, error=f"Failed to set kubectl context to minikube: {e}"
            )

        namespace = kwargs.get("namespace") or context.get("namespace", "default")

        # Update context with minikube configuration
        minikube_config = {
            "namespace": namespace,
        }

        return BaseResponse(
            success=True,
            message=(
                f"Minikube platform initialized successfully in namespace {namespace}"
            ),
            namespace=namespace,
            data=minikube_config,
        )

    @with_context
    def deploy(self, context: Dict[str, Any], path: Path, **kwargs) -> Dict[str, Any]:
        """
        Deploy the application to the minikube environment.

        Args:
            path: The path to the application
            **kwargs: Additional arguments
        """
        try:
            deploy_to_minikube(path, **kwargs)
            return BaseResponse(
                success=True,
                message="Deployment successful",
            )
        except Exception as e:
            return BaseResponse(
                success=False, error=str(e), message="Deployment failed"
            )

    def delete(self, context: Dict[str, Any]) -> BaseResponse:
        return self.k8s.delete(context=context)

    def logs(self, context: Dict[str, Any]) -> BaseResponse:
        return self.k8s.logs(context=context)

    def open(
        self,
        context: Dict[str, Any],
        path: str,
        port: int = 8080,
        url: Optional[str] = None,
    ) -> BaseResponse:
        return self.k8s.open(context=context, path=path, port=port, url=url)

    def status(self, context: Dict[str, Any]) -> BaseResponse:
        return self.k8s.status(context=context)
