from typing import Optional, Dict, Any
from sfai.context.manager import ContextManager
from sfai.platform.registry import PLATFORM_REGISTRY
from sfai.core.response_models import BaseResponse
from sfai.platform.switch import switch


def init(
    platform: Optional[str] = None, environment: str = "default", **kwargs
) -> Dict[str, Any]:
    """
    Initialize or update the active platform environment.

    Args:
        platform: Optional[str]
            Platform provider (e.g., 'local', 'heroku', 'aws')
        environment: str
            Environment name (defaults to "default")
        **kwargs:
            Provider-specific config options (app_name, routing, etc.)

    Returns:
        Dict with success or error details.
    """
    ctx_mgr = ContextManager()
    context = ctx_mgr.read_context()

    if not context:
        return BaseResponse(
            success=False,
            error="No app context found. Please run `sfai app init` first.",
        )

    platform = platform or context.get("active_platform")
    if not platform:
        return BaseResponse(success=False, error="No platform provided.")

    provider = PLATFORM_REGISTRY.get(platform)
    if not provider:
        return BaseResponse(success=False, error=f"Unsupported provider: {platform}")

    # Handle app_name logic
    base_app_name = context.get("app_name")
    user_provided_app_name = kwargs.get("app_name")

    # Always append environment suffix for non-default environments
    if environment != "default":
        # Use user provided name if available, otherwise use base app name
        app_name_base = user_provided_app_name or base_app_name
        environment_app_name = f"{app_name_base}-{environment}"
    else:
        # For default environment, use base app name or user provided name
        environment_app_name = user_provided_app_name or base_app_name

    # Create a clean context with only basic app info and environment-specific app name
    # This ensures providers start fresh for new environments
    environment_context = {
        "app_name": environment_app_name,
        "active_platform": platform,
        "active_environment": environment,
    }

    # Check if this environment already exists and add existing data if it does
    existing_env_context = ctx_mgr.read_context(platform, environment)
    if existing_env_context:
        # Merge existing environment-specific data but preserve our calculated app_name
        environment_context.update(existing_env_context)
        environment_context["app_name"] = (
            environment_app_name  # Always use our calculated app name
        )

    # Remove app_name from kwargs to prevent it from overriding our
    # environment-specific logic
    provider_kwargs = kwargs.copy()
    provider_kwargs.pop("app_name", None)

    try:
        result = provider.init(context=environment_context, **provider_kwargs)
        if not isinstance(result, BaseResponse):
            return BaseResponse(
                success=False, error="Invalid result from provider handler"
            )

        # Update platform with environment-specific configuration
        if result.success and hasattr(result, "data") and result.data:
            ctx_mgr.update_platform(platform, result.data, environment)

            # Switch to the newly initialized environment
            switch(platform, environment)

        return result.with_update(
            platform=platform,
            environment=environment,
            app_name=base_app_name,  # Return the original app name in response
        )
    except Exception as e:
        return BaseResponse(success=False, error=str(e))
