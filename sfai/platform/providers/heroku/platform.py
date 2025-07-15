import subprocess
import json
import logging
from typing import Dict, Any, Optional
from sfai.core.base import BasePlatform
from sfai.context.manager import ContextManager
from sfai.core.response_models import BaseResponse
from sfai.platform.providers.heroku.utils.checks import (
    is_heroku_cli_installed,
    check_heroku_auth_status,
    heroku_login,
)
from sfai.platform.providers.heroku.utils.deploy import (
    create_heroku_app,
    deploy_to_heroku,
)
from sfai.platform.providers.heroku.utils.deploy import COLOR_PATTERN
from sfai.core.decorators import with_context

logger = logging.getLogger(__name__)
ctx_mgr = ContextManager()


class HerokuPlatform(BasePlatform):
    def init(
        self, context: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Dict[str, Any]:
        if not is_heroku_cli_installed():
            return BaseResponse(success=False, error="Heroku CLI not installed.")

        app_name = (
            kwargs.get("app_name").lower()
            if kwargs.get("app_name")
            else context.get("app_name", "").lower()
        )
        team_name = kwargs.get("team_name") or context.get("team_name", "")
        private_space = kwargs.get("private_space") or context.get("private_space", "")
        deployment_type = kwargs.get("deployment_type") or "buildpack"
        routing = kwargs.get("routing") or "public"

        auth_success, _ = check_heroku_auth_status()
        if not auth_success:
            login_success, msg = heroku_login()
            if not login_success:
                return BaseResponse(success=False, error=f"Heroku login failed: {msg}")

        try:
            result = subprocess.run(
                ["heroku", "apps:info", "--app", app_name, "--json"],
                check=True,
                capture_output=True,
                text=True,
            )
            if "forbidden" in result.stderr:
                logger.warning(
                    "App already exists but you do not have access to it, "
                    "creating new app with random prefix"
                )
                # Create new app when access is forbidden
                return create_heroku_app(
                    app_name, team_name, private_space, routing, deployment_type
                )
            else:
                # App exists and have access
                app_info = json.loads(COLOR_PATTERN.sub("", result.stdout))
                logger.warning(f"App already exists, using existing app {app_name}")

                heroku_config = {
                    "app_name": app_info["app"]["name"],
                    "public_url": app_info["app"]["web_url"],
                    "git_url": app_info["app"]["git_url"],
                    "team_name": app_info["app"]["team"],
                    "private_space": app_info["app"]["space"],
                    "deployment_type": app_info["app"]["build_stack"]["name"],
                    "routing": (
                        "public"
                        if app_info["app"]["internal_routing"] is None
                        else (
                            "internal"
                            if app_info["app"]["internal_routing"]
                            else "public"
                        )
                    ),
                }

                return BaseResponse(
                    success=True,
                    message=f"Initialized with existing Heroku app {app_name}.",
                    data=heroku_config,
                )
        except subprocess.CalledProcessError:
            # Create new app when command fails
            return create_heroku_app(
                app_name, team_name, private_space, routing, deployment_type
            )

    @with_context
    def deploy(self, context: Dict[str, Any], **kwargs) -> BaseResponse:
        deploy_to_heroku(**kwargs)
        return BaseResponse(
            success=True,
            message="Deployment successful",
            public_url=context.get("public_url"),
        )

    @with_context
    def delete(self, context: Dict[str, Any]) -> BaseResponse:
        subprocess.run(
            [
                "heroku",
                "apps:destroy",
                "--app",
                context.get("app_name"),
                "--confirm",
                context.get("app_name"),
            ],
            check=False,
        )
        ctx_mgr.clear_platform_keys("heroku", ["app_name", "public_url", "git_url"])
        return BaseResponse(
            success=True,
            message="App deleted successfully",
        )

    @with_context
    def status(self, context: Dict[str, Any]) -> BaseResponse:
        subprocess.run(["heroku", "ps", "--app", context.get("app_name")], check=False)
        return BaseResponse(success=True, message="App status checked successfully")

    @with_context
    def logs(self, context: Dict[str, Any]) -> BaseResponse:
        subprocess.run(
            ["heroku", "logs", "--app", context.get("app_name")], check=False
        )
        return BaseResponse(success=True, message="Logs fetched successfully")

    @with_context
    def open(
        self, context: Dict[str, Any], path: str = "/docs", url: Optional[str] = None
    ) -> BaseResponse:
        if not url:
            url = context.get("public_url")
        if not url:
            return BaseResponse(success=False, error="No public URL found.")
        full_url = f"{url.rstrip('/')}{path}"
        return BaseResponse(
            success=True, message=f"App opened successfully: {full_url}", url=full_url
        )
