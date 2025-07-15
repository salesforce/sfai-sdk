from typing import Optional
from sfai.context.manager import ContextManager
from sfai.core.response_models import BaseResponse


def list(service: Optional[str] = None) -> BaseResponse:
    """
    List all profiles for one or all services.

    Args:
        service: Service name, or None to list all services

    Returns:
        BaseResponse with operation result and profiles list
    """
    ctx_mgr = ContextManager()

    try:
        if service:
            # Use the ContextManager method for single service
            profiles = ctx_mgr.list_service_profiles(service)
            if not profiles:
                return BaseResponse(
                    success=False, error=f"No profiles found for service: {service}"
                )
            return BaseResponse(success=True, service=service, profiles=profiles)
        else:
            # Get all services and their profiles
            context = ctx_mgr._load_json(ctx_mgr.global_context_file)
            all_profiles = context.get("service_profiles", {})

            if not all_profiles:
                return BaseResponse(success=True, profiles={})

            result = {}
            for svc in all_profiles.keys():
                result[svc] = ctx_mgr.list_service_profiles(svc)

            return BaseResponse(success=True, profiles=result)
    except Exception as e:
        return BaseResponse(success=False, error=f"Failed to list profiles: {e!s}")
