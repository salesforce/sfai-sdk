import logging
from typing import Dict, Any, Optional
from pathlib import Path
import boto3
from sfai.core.base import BasePlatform
from sfai.context.manager import ContextManager
from sfai.core.response_models import BaseResponse
from sfai.platform.providers.eks.utils.checks import (
    _is_aws_cli_installed,
    _verify_aws_credentials,
    _verify_eks_cluster,
    _verify_namespace,
)
from sfai.platform.providers.eks.utils.helpers import (
    _get_ecr_repository,
    _update_kubeconfig,
    get_public_url,
)
from sfai.platform.providers.kubernetes.platform import K8sPlatform
from sfai.core.decorators import with_context
from sfai.platform.providers.kubernetes.utils.helpers import get_app_version
from sfai.platform.providers.eks.utils.helpers import _build_and_push_image
from rich.console import Console
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound

logger = logging.getLogger(__name__)
ctx_mgr = ContextManager()
console = Console()


class EKSPlatform(BasePlatform):
    def __init__(self):
        self.k8s = K8sPlatform(env="aws")

    def init(self, context: Optional[Dict[str, Any]] = None, **kwargs) -> BaseResponse:
        """
        Initialize AWS platform for deploying to existing EKS cluster.

        Args:
            context (Dict[str, Any]): The context dictionary containing the
                current state of the application.
            **kwargs: Additional keyword arguments.

        Returns:
            BaseResponse: A response object containing the result of the initialization.
        """

        # Check if AWS CLI is installed
        if not _is_aws_cli_installed():
            return BaseResponse(
                success=False,
                error=(
                    "AWS CLI not installed. Please install AWS CLI and "
                    "configure credentials."
                ),
            )

        # Get parameters from kwargs or prompt for them
        cluster_name = kwargs.get("cluster_name") or context.get("cluster_name")
        namespace = kwargs.get("namespace") or context.get("namespace", "default")
        ecr_repo = kwargs.get("ecr_repo") or context.get("ecr_repo")
        region = kwargs.get("region") or context.get("region")
        profile = kwargs.get("profile") or context.get("profile", "default")
        service_account = kwargs.get("service_account") or context.get(
            "service_account"
        )
        force = kwargs.get("force", False)

        # Validate required parameters
        if not cluster_name:
            return BaseResponse(
                success=False,
                error=(
                    "EKS cluster name is required. Please provide "
                    "--cluster-name parameter."
                ),
            )

        if not ecr_repo:
            return BaseResponse(
                success=False,
                error=(
                    "ECR repository URI is required. Please provide "
                    "--ecr-repo parameter."
                ),
            )

        if not region:
            return BaseResponse(
                success=False,
                error="AWS region is required. Please provide --region parameter.",
            )

        # Skip if platform already initialized
        if context.get("cluster_name") and context.get("ecr_repo") and not force:
            return BaseResponse(
                success=False,
                error=(
                    f"AWS platform already initialized with cluster "
                    f"{context.get('cluster_name')}, use force=True to reinitialize"
                ),
            )

        # Verify AWS credentials
        if not _verify_aws_credentials(profile):
            return BaseResponse(
                success=False,
                error=(
                    "AWS credentials not found or expired. Please configure "
                    "your credentials."
                ),
            )

        # Verify EKS cluster exists and is accessible
        cluster_info = _verify_eks_cluster(cluster_name, region, profile)
        if not cluster_info:
            return BaseResponse(
                success=False,
                error=(
                    f"EKS cluster '{cluster_name}' not found or not accessible "
                    f"in region '{region}'"
                ),
            )

        # Verify ECR repository exists
        ecr_uri = _get_ecr_repository(ecr_repo, region, profile)
        if not ecr_uri:
            return BaseResponse(
                success=False,
                error=(
                    f"ECR repository '{ecr_repo}' not found or not accessible "
                    f"in region '{region}'"
                ),
            )

        # Update kubeconfig for the EKS cluster
        if not _update_kubeconfig(cluster_name, region, profile):
            return BaseResponse(
                success=False,
                error=f"Failed to update kubeconfig for EKS cluster '{cluster_name}'",
            )

        # Verify namespace exists or create it
        if not _verify_namespace(namespace):
            return BaseResponse(
                success=False, error=f"Failed to verify namespace '{namespace}'"
            )

        # Store AWS configuration
        aws_config = {
            "cluster_name": cluster_name,
            "namespace": namespace,
            "ecr_repo": ecr_repo,
            "ecr_repo_uri": ecr_uri,
            "region": region,
            "profile": profile,
            "cluster_endpoint": cluster_info.get("endpoint"),
            "cluster_arn": cluster_info.get("arn"),
            "cluster_version": cluster_info.get("version"),
        }

        if service_account:
            aws_config["service_account"] = service_account

        return BaseResponse(
            success=True,
            message=(
                f"AWS platform initialized successfully for EKS cluster "
                f"'{cluster_name}' in region '{region}'"
            ),
            cluster_name=cluster_name,
            namespace=namespace,
            region=region,
            data=aws_config,
        )

    @with_context
    def deploy(self, context: Dict[str, Any], path: Path, **kwargs) -> BaseResponse:
        """
        Deploy the application to EKS cluster using Helm.

        Args:
            context: Application context containing EKS configuration
            path: The path to the Helm chart
            **kwargs: Additional arguments
        """
        app_name = context.get("app_name")
        cluster_name = context.get("cluster_name")
        namespace = context.get("namespace", "default")
        ecr_repo = context.get("ecr_repo")
        ecr_repo_uri = context.get("ecr_repo_uri")
        region = context.get("region")
        profile = context.get("profile", "default")
        version = context.get("version") or get_app_version(path)

        if not _verify_aws_credentials(profile=profile):
            return BaseResponse(
                success=False,
                error=(
                    "AWS credentials not found or expired. Please configure "
                    "your credentials."
                ),
            )

        if not cluster_name:
            return BaseResponse(
                success=False,
                error=(
                    "EKS cluster not configured. Please run "
                    "'sfai platform init aws' first."
                ),
            )
        session = boto3.Session(profile_name=profile, region_name=region)
        ecr = session.client("ecr")
        try:
            ecr.describe_images(
                repositoryName=ecr_repo, imageIds=[{"imageTag": version}]
            )
            logger.info(
                "Image already exists in ECR. Skipping build and push. "
                "update version in version.json to build and push a new image."
            )
        except ecr.exceptions.ImageNotFoundException:
            build_result = _build_and_push_image(
                path, ecr_repo_uri, region, image_tag=version, profile=profile
            )
            if not build_result:
                return BaseResponse(
                    success=False, error="Failed to build and push Docker image to ECR"
                )
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ExpiredTokenException":
                return BaseResponse(
                    success=False,
                    error="AWS credentials expired. Please refresh your credentials.",
                )
            elif error_code == "UnauthorizedOperation":
                return BaseResponse(
                    success=False, error="Insufficient AWS permissions for ECR access."
                )
            else:
                return BaseResponse(
                    success=False, error=f"AWS error: {e.response['Error']['Message']}"
                )
        except NoCredentialsError:
            return BaseResponse(
                success=False,
                error="AWS credentials not found. Please configure your credentials.",
            )
        except ProfileNotFound:
            return BaseResponse(
                success=False, error=f"AWS profile '{profile}' not found."
            )

        context["helm_set"] = {
            "image.repository": ecr_repo_uri,
            "image.tag": version,
            "image.pullPolicy": "IfNotPresent",
        }

        # helm install/upgrade
        console.print(f"Deploying {app_name}:{version} to namespace {namespace}...")
        result = self.k8s.deploy(context=context, path=path, **kwargs)

        if result.success:
            public_url = get_public_url(app_name, namespace)
            if public_url:
                ctx_mgr.update_platform(
                    platform="eks",
                    values={"public_url": public_url, "image_tag": version},
                    environment=context.get("active_environment", "default"),
                )
            else:
                ctx_mgr.update_platform(
                    platform="eks",
                    values={"image_tag": version},
                    environment=context.get("active_environment", "default"),
                )
            return BaseResponse(
                success=True,
                message=f"Deployed {app_name}:{version} to {namespace}",
                public_url=public_url,
            )
        else:
            return BaseResponse(
                success=False, error=result.error, message="Helm deployment failed"
            )

    @with_context
    def delete(self, context: Dict[str, Any]) -> BaseResponse:
        if not _verify_aws_credentials(profile=context.get("profile", "default")):
            return BaseResponse(
                success=False,
                error=(
                    "AWS credentials not found or expired. Please configure "
                    "your credentials."
                ),
            )
        return self.k8s.delete(context=context)

    @with_context
    def logs(self, context: Dict[str, Any]) -> BaseResponse:
        """Get logs from the application pods."""
        if not _verify_aws_credentials(profile=context.get("profile", "default")):
            return BaseResponse(
                success=False,
                error=(
                    "AWS credentials not found or expired. Please configure "
                    "your credentials."
                ),
            )
        return self.k8s.logs(context=context)

    @with_context
    def open(
        self,
        context: Dict[str, Any],
        path: str,
        port: int = 8080,
        url: Optional[str] = None,
    ) -> BaseResponse:
        if not url:
            url = context.get("public_url")
            return BaseResponse(
                success=True, url=url, message=f"Opened app public url at {url}"
            )
        if not url:
            result = super().open(context=context, path=path, port=port, url=url)
            return BaseResponse(
                success=True, url=result.url, message=f"Port forwarded to {url}"
            )
        else:
            return BaseResponse(
                success=False, error=result.error, message="Failed to open app"
            )

    @with_context
    def status(self, context: Dict[str, Any]) -> BaseResponse:
        if not _verify_aws_credentials(profile=context.get("profile", "default")):
            return BaseResponse(
                success=False,
                error=(
                    "AWS credentials not found or expired. Please configure "
                    "your credentials."
                ),
            )
        return self.k8s.status(context=context)
