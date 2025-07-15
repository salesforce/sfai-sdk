import subprocess
import logging
import boto3
from typing import Dict, Any
from kubernetes import client, config
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)


def _is_aws_cli_installed() -> bool:
    """Check if AWS CLI is installed."""
    try:
        subprocess.run(["aws", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _verify_aws_credentials(profile: str = "default") -> bool:
    """Verify AWS credentials are configured and valid."""
    try:
        session = boto3.Session(profile_name=profile)
        logger.warning(f"Verifying AWS credentials for profile: {profile}")
        sts = session.client("sts")
        sts.get_caller_identity()
        return True
    except Exception as e:
        logger.error(f"Error verifying AWS credentials: {e}")
        return False


def _verify_eks_cluster(
    cluster_name: str, region: str, profile: str = "default"
) -> Dict[str, Any]:
    """Verify EKS cluster exists and return cluster information."""
    try:
        session = boto3.Session(profile_name=profile, region_name=region)
        eks = session.client("eks")
        cluster = eks.describe_cluster(name=cluster_name)["cluster"]

        return {
            "endpoint": cluster.get("endpoint"),
            "arn": cluster.get("arn"),
            "version": cluster.get("version"),
            "status": cluster.get("status"),
        }
    except Exception as e:
        logger.error(f"Error verifying EKS cluster: {e}")
        return None


def _verify_namespace(namespace: str) -> bool:
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()

        # Check if namespace exists
        v1.read_namespace(name=namespace)
        return True
    except ApiException as e:
        logger.error(f"Error verifying namespace: {e}")
        return False
