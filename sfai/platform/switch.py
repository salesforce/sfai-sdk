from sfai.context.manager import ContextManager
from sfai.core.response_models import BaseResponse

ctx_mgr = ContextManager()


def switch(
    cloud: str,
) -> BaseResponse:
    """
    Switch to a different platform.

    Args:
        cloud: str
            Platform provider (e.g., 'local', 'heroku', 'aws')
    Returns:
        BaseResponse
    """
    try:
        context = ctx_mgr.read_context()
        if not context:
            return BaseResponse(
                success=False,
                error="No app context found. Please run `sfai app init` first.",
            )

        env_data = ctx_mgr.read_context(cloud)
        if not env_data:
            return BaseResponse(
                success=False, error=f"Platform '{cloud}' is not initialized yet."
            )

        # update the active environment
        ctx_mgr.update_platform(cloud, env_data)
        return BaseResponse(
            success=True,
            message=f"Switched to {cloud} platform",
            app_name=context.get("app_name"),
            platform=cloud,
        )
    except ValueError as e:
        return BaseResponse(
            success=False, error=f"Failed to switch to {cloud} platform: {e!s}"
        )
