from sfai.context.manager import ContextManager
from sfai.core.response_models import BaseResponse

ctx_mgr = ContextManager()


def switch(
    platform: str,
    environment: str = "default",
) -> BaseResponse:
    """
    Switch to a different platform.

    Args:
        platform: str
            Platform provider (e.g., 'local', 'heroku', 'aws')
        environment: str
            Environment to switch to
    Returns:
        BaseResponse
    """
    try:
        ctx_mgr = ContextManager()

        # Check if app context exists
        context = ctx_mgr.read_context()
        if not context:
            return BaseResponse(
                success=False,
                error="No app context found. Please run `sfai app init` first.",
            )

        # Check platform and environment status
        status = ctx_mgr.check_platform_environment(platform, environment)

        if not status["exists"]:
            if not status["platform_exists"]:
                # Platform doesn't exist
                available_platforms = status.get("available_platforms", [])
                if available_platforms:
                    platforms_str = ", ".join(available_platforms)
                    error_msg = (
                        f"Platform '{platform}' is not initialized. "
                        f"Available platforms: {platforms_str}"
                    )
                else:
                    error_msg = (
                        f"Platform '{platform}' is not initialized. "
                        f"No platforms configured yet."
                    )
                error_msg += (
                    f"\nRun: sfai platform init --platform {platform} "
                    f"--environment {environment}"
                )
            else:
                # Platform exists but environment doesn't
                available_envs = status.get("available_environments", [])
                if available_envs:
                    envs_str = ", ".join(available_envs)
                    error_msg = (
                        f"Environment '{environment}' not found for platform "
                        f"'{platform}'. Available environments: {envs_str}"
                    )
                else:
                    error_msg = (
                        f"Environment '{environment}' not found for platform "
                        f"'{platform}'. No environments configured yet."
                    )
                error_msg += (
                    f"\nRun: sfai platform init --platform {platform} "
                    f"--environment {environment}"
                )

            return BaseResponse(
                success=False,
                error=error_msg,
            )

        # Environment exists, get the data and switch
        env_data = ctx_mgr.read_context(platform, environment)
        if not env_data:
            return BaseResponse(
                success=False,
                error=(
                    f"Failed to load configuration for platform '{platform}' "
                    f"environment '{environment}'."
                ),
            )

        # Update the active environment
        ctx_mgr.update_platform(platform, env_data, environment)
        return BaseResponse(
            success=True,
            platform=platform,
            environment=environment,
        )
    except ValueError as e:
        return BaseResponse(
            success=False,
            error=(
                f"Failed to switch to {platform} platform, {environment} "
                f"environment: {e!s}"
            ),
        )
