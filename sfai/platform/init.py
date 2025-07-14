from typing import Optional, Dict, Any
from sfai.context.manager import ContextManager
from sfai.platform.registry import PLATFORM_REGISTRY
from sfai.core.response_models import BaseResponse


def init(cloud: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Initialize or update the active platform environment.

    Args:
        cloud: Optional[str]
            Platform provider (e.g., 'local', 'heroku', 'aws')
        **kwargs:
            Provider-specific config options (app_name, routing, etc.)

    Returns:
        Dict with success or error details.
    """
    ctx_mgr = ContextManager()
    context = ctx_mgr.read_context()

    if not context:
        return BaseResponse(
            success=False,
            error="No app context found. Please run `sfai app init` first.",
        )

    cloud = cloud or context.get("active_platform")
    if not cloud:
        return BaseResponse(success=False, error="No platform provided.")

    provider = PLATFORM_REGISTRY.get(cloud)
    if not provider:
        return BaseResponse(success=False, error=f"Unsupported provider: {cloud}")

    try:
        result = provider.init(context=context, **kwargs)
        if not isinstance(result, BaseResponse):
            return BaseResponse(
                success=False, error="Invalid result from provider handler"
            )
        return result.with_update(platform=cloud, app_name=context.get("app_name"))
    except Exception as e:
        return BaseResponse(success=False, error=str(e))
