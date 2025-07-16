from typing import Optional
from sfai.context.manager import ContextManager
from sfai.platform.switch import switch
from sfai.core.response_models import BaseResponse


def determine_platform_and_environment(
    platform: Optional[str] = None, environment: Optional[str] = None
) -> BaseResponse:
    """
    Determine the platform and environment to use, switching if necessary.

    Args:
        platform: Desired platform (optional)
        environment: Desired environment (optional)

    Returns:
        A BaseResponse object containing the active platform, active environment,
        and indicating the success or failure of any switch operation.
    """
    ctx_mgr = ContextManager()
    context = ctx_mgr.read_context()
    if not context:
        return BaseResponse(
            success=False,
            error="No app context found. Run `sfai init` to initialize an app.",
        )

    current_platform = context.get("active_platform")
    current_environment = context.get("active_environment")

    if platform:
        if environment is None:
            platform_context = ctx_mgr.read_context(platform)
            if platform_context:
                environment = platform_context.get("active_environment", "default")
            else:
                environment = "default"

        if platform != current_platform or environment != current_environment:
            switch_result = switch(platform, environment)
            if not switch_result.success:
                return switch_result
            context = ctx_mgr.read_context(platform, environment)
    elif environment is not None and current_environment != environment:
        switch_result = switch(current_platform, environment)
        if not switch_result.success:
            return switch_result
        context = ctx_mgr.read_context(current_platform, environment)
    else:
        environment = current_environment

    active_platform = context.get("active_platform")
    return BaseResponse(success=True, platform=active_platform, environment=environment)
