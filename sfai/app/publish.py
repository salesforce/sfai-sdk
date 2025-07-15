from typing import Dict, Any
from sfai.integrations.registry import INTEGRATION_REGISTRY
from sfai.context.manager import ContextManager
from sfai.core.response_models import BaseResponse


def publish(service: str = "mulesoft", **kwargs) -> Dict[str, Any]:
    try:
        ctx_mgr = ContextManager()
        ctx = ctx_mgr.read_context()
        if not ctx:
            return BaseResponse(
                success=False,
                error="No App context found",
            )

        integration = INTEGRATION_REGISTRY.get(service)
        if not integration:
            return BaseResponse(
                success=False,
                error=f"Integration for {service} not found",
            )

        result = integration.publish(ctx=ctx, **kwargs)
        return result.with_update(
            app_name=ctx.get("app_name"),
            integration=service,
        )
    except ValueError as e:
        return BaseResponse(success=False, error=f"Context validation error: {e!s}")
