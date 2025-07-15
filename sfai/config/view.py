from sfai.context.manager import ContextManager
from sfai.config.utils.validate import profile_exists
from sfai.core.response_models import BaseResponse


def view(service: str, profile_name: str = "default") -> BaseResponse:
    """
    View details of a service profile.

    Args:
        service: Service name
        profile_name: Profile name to view

    Returns:
        BaseResponse
    """
    ctx_mgr = ContextManager()

    # Check if profile exists
    exists, error = profile_exists(service, profile_name)
    if not exists:
        return BaseResponse(
            success=False,
            error=error,
            service=service,
            profile_name=profile_name,
        )

    # Get the profile
    profile = ctx_mgr.get_service_profile(service, profile_name)

    # Create a safe version with masked secrets
    safe_profile = {}
    for key, value in profile.items():
        if any(s in key.lower() for s in ["secret", "password", "key"]):
            # Mask the secret value, showing just the first and last character
            safe_profile[key] = (
                f"{value[0]}{'*' * (len(str(value)) - 2)}{value[-1]}"
                if len(str(value)) > 4
                else "****"
            )
        else:
            safe_profile[key] = value
    return BaseResponse(
        success=True,
        message=f"Profile '{profile_name}' for service '{service}' is shown below",
        profile_name=profile_name,
        service=service,
        data=safe_profile,
    )
