from sfai.context.manager import ContextManager
from sfai.platform.registry import PLATFORM_REGISTRY
from sfai.core.response_models import BaseResponse
from typing import Optional
from sfai.app.utils.helpers import determine_platform_and_environment


def open(
    path: str = "/docs",
    port: int = 8080,
    tunnel: bool = False,
    url: Optional[str] = None,
    platform: Optional[str] = None,
    environment: Optional[str] = None,
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
        # Load current context
        ctx_mgr = ContextManager()

        # Determine the platform and environment to use
        response = determine_platform_and_environment(platform, environment)
        if not response.success:
            return response

        # Validate platform provider
        active_platform = response.platform
        active_environment = response.environment

        # Read the updated context for the determined platform and environment
        context = ctx_mgr.read_context(active_platform, active_environment)
        if not context:
            return BaseResponse(
                success=False,
                error=(
                    f"Failed to read context for platform '{active_platform}' "
                    f"and environment '{active_environment}'"
                ),
            )

        provider = PLATFORM_REGISTRY.get(active_platform)
        if not provider:
            return BaseResponse(
                success=False, error=f"Unsupported provider: {active_platform}"
            )

        # Validate tunnel requirements
        if tunnel and active_platform != "local":
            return BaseResponse(
                success=False,
                error="Tunneling is only supported in local environment.",
            )

        # Execute the open operation
        result = provider.open(context=context, path=path, url=url)

        # Return result with context metadata
        return result.with_update(
            app_name=context.get("app_name"),
            platform=active_platform,
            environment=active_environment,
        )

    except ValueError as e:
        return BaseResponse(success=False, error=f"Context validation error: {e!s}")
