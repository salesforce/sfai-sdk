from typing import Dict, Any, Optional
from sfai.context.manager import ContextManager
from sfai.config.utils.validate import validate
from sfai.core.response_models import BaseResponse


def init(
    service: str,
    config: Optional[Dict[str, Any]] = None,
    profile_name: str = "default",
    env: Optional[str] = None,
    **kwargs,
) -> BaseResponse:
    """
    Initialize configuration for a service.

    Args:
        service: Service name (e.g., "mulesoft")
        credentials: Dictionary of credentials for the service
        profile_name: Profile name to store credentials under
        env: Environment to set as active (uses current if None)
        **kwargs: pass values directly to the service provider

    Returns:
        BaseResponse
    """
    ctx_mgr = ContextManager()

    # Read current context to get app info if needed
    context = ctx_mgr.read_context()
    if not context:
        return BaseResponse(
            success=False, error="No app context found. Initialize an app first."
        )

    app_name = context.get("app_name")
    current_platform = env or context.get("active_platform")

    if config is None and not kwargs:
        return BaseResponse(success=False, error="No configuration provided.")
    config = config or kwargs
    if not app_name or not current_platform:
        return BaseResponse(
            success=False, error="App name or platform missing in context."
        )

    # Validate credentials
    result = validate(service, config)
    if not result.success:
        return result.with_update(
            service=service,
            profile_name=profile_name,
        )

    try:
        # Save the service profile
        ctx_mgr.add_service_profile(service, profile_name, config)

        # Update the environment to use this profile
        ctx_mgr.update_platform(current_platform, {service: {"profile": profile_name}})

        return BaseResponse(
            success=True,
            service=service,
            profile_name=profile_name,
        )
    except ValueError as e:
        return BaseResponse(success=False, error=f"Failed to save credentials: {e!s}")
