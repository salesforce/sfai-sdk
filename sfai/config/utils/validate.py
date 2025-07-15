from typing import Dict, Any, Tuple
from sfai.config.registry import SERVICE_CONFIG
from sfai.context.manager import ContextManager
from sfai.core.response_models import BaseResponse

ctx_mgr = ContextManager()


def _get_service_schema(service: str):
    """Get the schema for a service."""
    return SERVICE_CONFIG.get(service)


def _get_schema_fields(service: str) -> Dict[str, str]:
    """Get the schema fields with their descriptions."""
    schema = _get_service_schema(service)
    if not schema:
        return {}

    # Get field info from Pydantic model
    fields = {}
    for field_name, field in schema.model_fields.items():
        description = field.description or field_name.replace("_", " ").title()
        fields[field_name] = description
    return fields


def validate(service: str, config: Dict[str, Any]) -> BaseResponse:
    """
    Validate configuration against service schema.

    Args:
        service: Service name
        config: Configuration to validate

    Returns:
        BaseResponse with validation result
    """
    schema = _get_service_schema(service)
    if not schema:
        return BaseResponse(success=False, error=f"Invalid service: {service}")

    try:
        # Validate using Pydantic model
        schema(**config)
        return BaseResponse(success=True)
    except Exception as e:
        return BaseResponse(success=False, error=f"Invalid configuration: {e!s}")


def profile_exists(service: str, profile_name: str) -> Tuple[bool, str]:
    """Check if a profile exists for a service."""
    profiles = ctx_mgr.list_service_profiles(service)
    if not profiles:
        return False, f"No profiles found for service: {service}"
    if profile_name not in profiles:
        return False, f"Profile {profile_name} not found for service {service}"
    return True, ""
