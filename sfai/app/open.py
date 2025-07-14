from sfai.context.manager import ContextManager
from sfai.platform.registry import PLATFORM_REGISTRY
from sfai.core.response_models import BaseResponse
from typing import Optional
from sfai.platform.switch import switch


def open(
    path: str = "/docs",
    port: int = 8080,
    tunnel: bool = False,
    url: str | None = None,
    platform: Optional[str] = None,
) -> BaseResponse:
    """
    Open the current app in the browser.

    Args:
        path: The path to open
        port: The port to open
        tunnel: Whether to use a tunnel
        url: The URL to open
    Returns:
        A dictionary containing the result of the open operation
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
        provider = PLATFORM_REGISTRY.get(active_platform)
        if not provider:
            return BaseResponse(
                success=False, error=f"Unsupported provider: {active_platform}"
            )

        if tunnel:
            if active_platform != "local":
                return BaseResponse(
                    success=False,
                    error="Tunneling is only supported in local environment.",
                )
        result = provider.open(context=context, path=path, url=url)
        return result.with_update(
            app_name=context.get("app_name"), platform=active_platform
        )
    except ValueError as e:
        return BaseResponse(success=False, error=f"Context validation error: {e!s}")
