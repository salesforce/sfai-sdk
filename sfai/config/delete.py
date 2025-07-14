from sfai.context.manager import ContextManager
from sfai.config.utils.validate import profile_exists
from sfai.core.response_models import BaseResponse


def delete(service: str, profile_name: str = "default") -> BaseResponse:
    """
    Delete a service profile.

    Args:
        service: Service name
        profile_name: Profile name to delete

    Returns:
        BaseResponse
    """
    ctx_mgr = ContextManager()

    # Check if profile exists
    exists, error = profile_exists(service, profile_name)
    if not exists:
        return BaseResponse(success=False, error=error)

    try:
        # Delete the profile
        ctx_mgr.delete_service_profile(service, profile_name)

        # Check if this profile is referenced in any environments
        context = ctx_mgr._load_json(ctx_mgr.context_file)
        environments = context.get("environments", {})

        # For each environment, check if it uses this profile
        for env_name, env_data in environments.items():
            if service in env_data and env_data[service].get("profile") == profile_name:
                # Remove the profile reference from this environment
                ctx_mgr.clear_platform_keys(env_name, [service])

        return BaseResponse(
            success=True,
            service=service,
            profile_name=profile_name,
            message=(
                f"Profile '{profile_name}' for service '{service}' has been deleted."
            ),
        )
    except Exception as e:
        return BaseResponse(success=False, error=f"Failed to delete profile: {e!s}")
