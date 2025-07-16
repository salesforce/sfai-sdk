from sfai.platform.registry import PLATFORM_REGISTRY
from sfai.context.manager import ContextManager
from sfai.core.response_models import BaseResponse
from typing import Optional
from sfai.app.utils.helpers import determine_platform_and_environment


def logs(
    platform: Optional[str] = None, environment: Optional[str] = None
) -> BaseResponse:
    """
    Show logs for the current app.

    Args:
        platform: Platform to show logs for
        environment: Environment to show logs for (uses active environment if None)

    Returns:
        BaseResponse: Response object containing logs
    """
    try:
        ctx_mgr = ContextManager()

        # Determine which platform and environment to use
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

        logs_response = provider.logs(context=context)

        return logs_response.with_update(
            app_name=context.get("app_name"),
            platform=active_platform,
            environment=active_environment,
        )
    except ValueError as e:
        return BaseResponse(success=False, error=f"Context validation error: {e!s}")
