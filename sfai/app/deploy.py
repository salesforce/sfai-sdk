from typing import Any, Optional
from sfai.context.manager import ContextManager
from sfai.platform.registry import PLATFORM_REGISTRY
from sfai.core.response_models import BaseResponse
from sfai.platform.switch import switch


def deploy(
    path: str = ".", platform: Optional[str] = None, **kwargs: Any
) -> BaseResponse:
    """
    Deploy an application to the configured environment.

    Args:
        path: Path to the application directory
        kwargs: Additional keyword arguments

    Returns:
        Dictionary with deployment status and details
    """
    try:
        # switch platform if provided
        if platform:
            switch_result = switch(platform)
            if not switch_result.success:
                return switch_result
        ctx_mgr = ContextManager()
        context = ctx_mgr.read_context()

        if not context:
            return BaseResponse(success=False, error="No app context found.")

        active_platform = context.get("active_platform")

        if not active_platform:
            return BaseResponse(
                success=False, error="No active platform found in context."
            )

        provider = PLATFORM_REGISTRY.get(active_platform)
        if not provider:
            return BaseResponse(
                success=False, error=f"Unsupported provider: {active_platform}"
            )

        result = provider.deploy(context=context, path=path, **kwargs)
        return result.with_update(
            app_name=context.get("app_name"), platform=active_platform
        )
    except ValueError as e:
        return BaseResponse(success=False, error=f"Context validation error: {e!s}")
