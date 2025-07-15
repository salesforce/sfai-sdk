from typing import Dict, Any
from sfai.context.manager import ContextManager
from sfai.config.utils.validate import profile_exists
from sfai.core.response_models import BaseResponse


def update(
    service: str, updates: Dict[str, Any], profile_name: str = "default"
) -> BaseResponse:
    """
    Update configuration for a service.

    Args:
        service: Service name
        updates: New values to update
        profile_name: Profile name to update

    Returns:
        BaseResponse
    """
    ctx_mgr = ContextManager()

    # Check if service and profile are valid
    result = profile_exists(service, profile_name)
    if not result.success:
        return result.with_update(
            service=service,
            profile_name=profile_name,
        )

    try:
        ctx_mgr.update_service_profile(service, profile_name, updates)
        return BaseResponse(
            success=True,
            service=service,
            profile_name=profile_name,
            updated_fields=list(updates.keys()),
        )
    except ValueError as e:
        return BaseResponse(
            success=False, error=f"Failed to update configuration: {e!s}"
        )
