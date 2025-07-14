from sfai.context.manager import ContextManager
from sfai.platform.registry import PLATFORM_REGISTRY
from sfai.core.response_models import BaseResponse
from typing import Optional
from sfai.platform.switch import switch


def status(platform: Optional[str] = None) -> BaseResponse:
    """
    Show the status of the current app from context.
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
            return BaseResponse(
                success=False,
                error="No app context found. Please run `sfai app init` first.",
            )

        active_platform = context.get("active_platform")
        provider = PLATFORM_REGISTRY.get(active_platform)
        if not provider:
            return BaseResponse(
                success=False, error=f"Unsupported provider: {active_platform}"
            )
        status_response = provider.status(context=context)
        return status_response.with_update(
            app_name=context.get("app_name"), platform=active_platform
        )
    except ValueError as e:
        return BaseResponse(success=False, error=f"Context validation error: {e!s}")
