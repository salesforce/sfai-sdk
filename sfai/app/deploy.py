from typing import Any, Optional
from sfai.context.manager import ContextManager
from sfai.platform.registry import PLATFORM_REGISTRY
from sfai.core.response_models import BaseResponse
from sfai.platform.switch import switch


def deploy(
    path: str = ".",
    platform: Optional[str] = None,
    environment: str = "default",
    **kwargs: Any,
) -> BaseResponse:
    """
    Deploy an application to the configured environment.

    Args:
        path: Path to the application directory
        platform: Platform to deploy to
        environment: Environment to deploy to
        kwargs: Additional keyword arguments

    Returns:
        Dictionary with deployment status and details
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

        result = provider.deploy(context=context, path=path, **kwargs)
        return result.with_update(
            app_name=context.get("app_name"),
            platform=active_platform,
            environment=environment,
        )
    except ValueError as e:
        return BaseResponse(success=False, error=f"Context validation error: {e!s}")
