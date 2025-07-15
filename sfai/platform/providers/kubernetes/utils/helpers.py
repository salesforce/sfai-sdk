import json
import re
from pathlib import Path


def get_app_version(path: Path) -> str:
    version_file = Path(path) / "version.json"
    if not version_file.exists():
        raise FileNotFoundError(f"version.json not found at {version_file}")

    version = json.loads(version_file.read_text()).get("version")
    if not version or not re.match(r"^\d+\.\d+\.\d+$", version):
        raise ValueError("Invalid or missing version in version.json (expected X.Y.Z)")

    return version
