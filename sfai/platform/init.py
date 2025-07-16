from typing import Optional, Dict, Any
from sfai.context.manager import ContextManager
from sfai.platform.registry import PLATFORM_REGISTRY
from sfai.core.response_models import BaseResponse
from sfai.platform.switch import switch


def init(
    platform: Optional[str] = None, environment: str = "default", **kwargs
) -> Dict[str, Any]:
    """
    Initialize or update the active platform environment.

    Args:
        platform: Optional[str]
            Platform provider (e.g., 'local', 'heroku', 'aws')
        environment: str
            Environment name (defaults to "default")
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

    platform = platform or context.get("active_platform")
    if not platform:
        return BaseResponse(success=False, error="No platform provided.")

    provider = PLATFORM_REGISTRY.get(platform)
    if not provider:
        return BaseResponse(success=False, error=f"Unsupported provider: {platform}")

    try:
        result = provider.init(context=context, environment=environment, **kwargs)
        if not isinstance(result, BaseResponse):
            return BaseResponse(
                success=False, error="Invalid result from provider handler"
            )

        if not result.success:
            return result

        # Save the platform configuration to context
        if result.data:
            ctx_mgr.update_platform(platform, result.data, environment)

        # Switch to the newly initialized environment
        switch_result = switch(platform, environment)
        if not switch_result.success:
            return switch_result

        return result.with_update(
            platform=platform,
            environment=environment,
            app_name=context.get("app_name"),
        )
    except Exception as e:
        return BaseResponse(success=False, error=str(e))
