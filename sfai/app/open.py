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
    environment: str = "default",
) -> BaseResponse:
    """
    Open the current app in the browser.

    Args:
        path: The path to open
        port: The port to open
        tunnel: Whether to use a tunnel
        url: The URL to open
        platform: Platform to open from (optional)
        environment: Environment to open from (defaults to "default")
    Returns:
        A dictionary containing the result of the open operation
    """
    try:
        ctx_mgr = ContextManager()
        context = ctx_mgr.read_context()
        if not context:
            return BaseResponse(success=False, error="No app context found.")

        # Determine which platform and environment to use
        if platform:
            # User specified platform - switch to it with specified environment
            switch_result = switch(platform, environment)
            if not switch_result.success:
                return switch_result
            context = ctx_mgr.read_context(platform, environment)
        else:
            # No platform specified - use current platform with specified environment
            current_platform = context.get("active_platform")
            current_environment = context.get("environment")

            # if user specified a different environment, switch to it
            if current_environment != environment:
                switch_result = switch(current_platform, environment)
                if not switch_result.success:
                    return switch_result
            context = ctx_mgr.read_context(current_platform, environment)

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
            app_name=context.get("app_name"),
            platform=active_platform,
            environment=environment,
        )
    except ValueError as e:
        return BaseResponse(success=False, error=f"Context validation error: {e!s}")
