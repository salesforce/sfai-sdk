from typing import Any, Optional
from sfai.context.manager import ContextManager
from sfai.platform.registry import PLATFORM_REGISTRY
from sfai.core.response_models import BaseResponse
from sfai.app.utils.helpers import determine_platform_and_environment


def deploy(
    path: str = ".",
    platform: Optional[str] = None,
    environment: Optional[str] = None,
    **kwargs: Any,
) -> BaseResponse:
    """
    Deploy an application to the configured environment.

    Args:
        path: Path to the application directory
        platform: Platform to deploy to
        environment: Environment to deploy to (uses active environment if None)
        kwargs: Additional keyword arguments

    Returns:
        Dictionary with deployment status and details
    """
    try:
        ctx_mgr = ContextManager()

        # determine the platform and environment to use
        response = determine_platform_and_environment(platform, environment)
        if not response.success:
            return response

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

        result = provider.deploy(context=context, path=path, **kwargs)
        return result.with_update(
            app_name=context.get("app_name"),
            platform=active_platform,
            environment=active_environment,
        )
    except ValueError as e:
        return BaseResponse(success=False, error=f"Context validation error: {e!s}")
