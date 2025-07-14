import shutil
from pathlib import Path
from typing import Optional


def scaffold_hello_app(dest_path, force=False, template: Optional[str] = None) -> None:
    dest_path = Path(dest_path).resolve()

    # Use the template parameter to choose which template to scaffold
    template_name = template or "fastapi_hello"
    template_path = (
        Path(__file__).resolve().parent / "../../core/templates" / template_name
    ).resolve()

    # Check if template exists
    if not template_path.exists():
        raise ValueError(f"Template '{template_name}' not found")

    dest_path.mkdir(parents=True, exist_ok=True)

    for item in template_path.iterdir():
        target = dest_path / item.name

        if not force and target.exists():
            continue

        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)
