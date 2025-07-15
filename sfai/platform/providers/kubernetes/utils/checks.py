import subprocess


def _is_kubectl_installed() -> bool:
    """Check if kubectl is installed."""
    try:
        subprocess.run(
            ["kubectl", "version", "--client"], capture_output=True, check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _is_helm_installed() -> bool:
    """Check if Helm is installed."""
    try:
        subprocess.run(["helm", "version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
