from typing import Optional
from sfai.platform.registry import PLATFORM_REGISTRY
from sfai.context.manager import ContextManager
from sfai.core.response_models import BaseResponse
from sfai.platform.switch import switch


def delete(
    platform: Optional[str] = None, environment: str = "default"
) -> BaseResponse:
    """
    Delete the current app from the context.

    Args:
        platform: Platform to delete from (optional)
        environment: Environment to delete from (defaults to "default")
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

        delete_response = provider.delete(context=context)
        return delete_response.with_update(
            app_name=context.get("app_name"),
            platform=active_platform,
            environment=environment,
        )
    except ValueError as e:
        return BaseResponse(success=False, error=f"Context validation error: {e!s}")
