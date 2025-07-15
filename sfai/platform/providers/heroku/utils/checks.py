import subprocess
import re
import random
import string
from typing import Tuple, Union
from pathlib import Path
from rich.console import Console

console = Console()

COLOR_PATTERN = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def generate_suffix(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def is_heroku_cli_installed() -> bool:
    """
    Check if the Heroku CLI is installed.
    """
    try:
        subprocess.run(
            ["heroku", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def is_heroku_repo(path: Union[str, Path]) -> bool:
    """Check if the given path is a Heroku repository.

    Args:
        path: The path to check.

    Returns:
        True if the path is a Heroku repository, False otherwise.
    """
    app_path = Path(path).resolve()

    try:
        # check if git is initialized
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=app_path,
            check=True,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            console.print("The current directory is not a git repository.")
            return False

        # check if heroku remote exists
        remotes = subprocess.run(
            ["git", "remote", "-v"],
            cwd=app_path,
            capture_output=True,
            text=True,
            check=False,
        )

        return bool(re.search(r"git\.heroku\.com", remotes.stdout))
    except Exception as e:
        console.print(f"Error checking Heroku repository: {e}")
        return False


def get_default_branch(path: Union[str, Path]) -> str:
    """Get the default branch name from git config.

    Args:
        path: The path to the git repository.

    Returns:
        The default branch name, or 'main' if not found.
    """
    app_path = Path(path).resolve()

    try:
        # Try to get the branch that HEAD is pointing to
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=app_path,
            capture_output=True,
            text=True,
            check=True,
        )
        if result.stdout.strip():
            return result.stdout.strip()

        # Fallback: try to get the default branch from config
        result = subprocess.run(
            ["git", "config", "--get", "init.defaultBranch"],
            cwd=app_path,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()

        # If still not found, return 'main' as default
        return "main"
    except Exception as e:
        console.print(f"Error getting default branch: {e}")
        return "main"


def check_heroku_auth_status() -> Tuple[bool, str]:
    """
    Check the authentication status of the Heroku CLI.

    Returns:
        Tuple[bool, str]
            A tuple containing a boolean indicating success and a message
    """
    try:
        result = subprocess.run(
            ["heroku", "auth:whoami"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        email = result.stdout.strip()
        return True, f"Authenticated as {email}"
    except Exception as e:
        return False, str(e)


def heroku_login() -> Tuple[bool, str]:
    """
    Prompt the user to login to Heroku.

    Returns:
        Tuple[bool, str]
            A tuple containing a boolean indicating success and a message
    """
    try:
        console.print("Opening browser to login to Heroku...")
        console.print(
            "If no browser opens, please run 'heroku login' manually in "
            "another terminal."
        )
        # Use shell=True to ensure it works properly across environments
        subprocess.run("heroku login", shell=True, check=False)
        return True, "Successfully logged in to Heroku"

    except Exception as e:
        console.print(f"Error during login: {e!s}")
        return False, f"Error during login process: {e!s}"
