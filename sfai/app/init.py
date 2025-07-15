from typing import Dict, Any, Optional
from pathlib import Path
from sfai.context.manager import ContextManager
from sfai.core.response_models import BaseResponse
from sfai.app.utils.scaffold import scaffold_hello_app
from sfai.constants import CONTEXT_DIR, CONTEXT_FILE


def init(
    app_name: Optional[str] = None, template: str = "fastapi_hello", force: bool = False
) -> Dict[str, Any]:
    """
    Initialize a new SFAI application.

    Args:
        app_name: Name of the application (defaults to directory name)
        template: Template to use for scaffolding (eg: fastapi_hello or flask_hello)
        force: Whether to force reinitialization if already initialized

    Returns:
        Dictionary with initialization status and details
    """
    # Use current directory as target path
    target_path = Path.cwd()

    # Determine app name (use directory name if not provided)
    app_name = app_name or target_path.name

    # Check if already initialized
    context_file = target_path / CONTEXT_DIR / CONTEXT_FILE.name
    context_exists = context_file.exists()

    if context_exists and not force:
        return BaseResponse(
            success=False,
            error=(
                f"App '{app_name}' is already initialized. "
                f"Use force=True to reinitialize."
            ),
            app_name=app_name,
        )

    try:
        # Initialize the app with the specified template
        scaffold_hello_app(target_path, force, template)

        # Update environment and register app
        ctx_mgr = ContextManager()
        ctx_mgr.update_platform(
            platform="local",
            environment="default",
            app_name=app_name,
            values={"app_name": app_name},
        )
        ctx_mgr.register_app(app_name, str(target_path))

        return BaseResponse(
            success=True,
            app_name=app_name,
            message=(
                f"App '{app_name}' initialized successfully with template '{template}'"
            ),
        )
    except (ValueError, Exception) as e:
        return BaseResponse(success=False, error=f"Failed to initialize app: {e!s}")
