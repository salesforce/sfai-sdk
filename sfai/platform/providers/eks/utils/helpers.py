import subprocess
from pathlib import Path
from rich.console import Console
from sfai.constants import DOCKER_EMOJI, PACKAGE_EMOJI, ROCKET_EMOJI, ERROR_EMOJI
import logging
import boto3
import json

console = Console()
logger = logging.getLogger(__name__)


def _get_ecr_repository(ecr_repo: str, region: str, profile: str = "default") -> str:
    """Verify ECR repository exists and is accessible."""
    try:
        session = boto3.Session(profile_name=profile)
        client = session.client("ecr", region_name=region)
        response = client.describe_repositories(repositoryNames=[ecr_repo])
        repo = response["repositories"][0]
        uri = repo["repositoryUri"]
        return uri
    except Exception as e:
        logger.error(f"Error verifying ECR repository: {e}")
        return None


def _update_kubeconfig(
    cluster_name: str, region: str, profile: str = "default"
) -> bool:
    """Update kubeconfig for the EKS cluster."""
    try:
        subprocess.run(
            [
                "aws",
                "eks",
                "update-kubeconfig",
                "--name",
                cluster_name,
                "--region",
                region,
                "--profile",
                profile,
            ],
            capture_output=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def _build_and_push_image(
    path: Path, ecr_repo_uri: str, region: str, image_tag: str, profile: str
) -> str:
    """Build Docker image and push to ECR."""
    try:
        full_image_name = f"{ecr_repo_uri}:{image_tag}"

        # Login to ECR
        cmd = (
            f"aws ecr get-login-password --region {region} --profile {profile} | "
            f"docker login --username AWS --password-stdin "
            f"{ecr_repo_uri.split('/')[0]}"
        )
        console.print("Logging in to ECR....")
        subprocess.run(cmd, shell=True, check=True)

        # Build image
        build_cmd = ["docker", "build", "-t", full_image_name, str(path)]
        console.print(f"{DOCKER_EMOJI} Building image....")
        subprocess.run(build_cmd, check=True)

        # Push image
        push_cmd = ["docker", "push", full_image_name]
        console.print(f"{PACKAGE_EMOJI} Pushing image....")
        subprocess.run(push_cmd, check=True)

        console.print(
            f"{ROCKET_EMOJI} Successfully built and pushed image: {full_image_name}"
        )
        return image_tag

    except subprocess.CalledProcessError as e:
        console.print(f"{ERROR_EMOJI} Failed to build and push image: {e}")
        return None


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
