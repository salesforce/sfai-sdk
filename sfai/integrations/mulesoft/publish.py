import os
from typing import Dict, Any
from sfai.context.manager import ContextManager
from sfai.core.base import BaseIntegration
from sfai.core.response_models import BaseResponse
from sfai.core.decorators import with_context
from sfai.integrations.mulesoft.utils import _get_mulesoft_client
from sfai.integrations.mulesoft.agentforce_utils import generate_openapi_from_app

ctx_mgr = ContextManager()


class MuleSoftIntegration(BaseIntegration):
    @with_context
    def publish(self, ctx: Dict[str, Any], **kwargs) -> BaseResponse:
        app_name = ctx.get("app_name")
        public_url = ctx.get("public_url")
        mulesoft_config = ctx.get("mulesoft", {})
        asset = mulesoft_config.get("asset", {})
        api = mulesoft_config.get("api", {})
        profile_name = kwargs.get("profile") or mulesoft_config.get("profile")

        if not profile_name:
            profiles = ctx_mgr.list_service_profiles("mulesoft")
            profile_name = profiles[0] if profiles else "default"

        profile = ctx_mgr.get_service_profile("mulesoft", profile_name)
        if not profile:
            return BaseResponse(
                success=False,
                error=f"Mulesoft profile {profile_name} not found",
            )

        # prepare the payload
        name = kwargs.get("name") or app_name
        version = kwargs.get("version") or asset.get("version")
        if not kwargs.get("version") and asset.get("version"):
            try:
                major, minor, patch = map(int, asset.get("version").split("."))
                patch += 1
                version = f"{major}.{minor}.{patch}"
            except ValueError as e:
                return BaseResponse(
                    success=False,
                    error=f"Error parsing version: {e}",
                )
        elif not version:
            version = "1.0.0"
        oas_file = kwargs.get("oas_file") or asset.get("oas_file", "openapi.yaml")

        # Check if we need to auto-generate OpenAPI spec
        if not os.path.exists(oas_file):
            # Try to auto-generate from app.py with AgentForce decorators
            generation_result = generate_openapi_from_app("app.py")
            if not generation_result.success:
                return BaseResponse(
                    success=False,
                    error=(
                        f"OAS file not found and auto-generation failed: "
                        f"{generation_result.error}"
                    ),
                )

            # Update oas_file to the generated file
            oas_file = generation_result.data.get("openapi_file", "openapi.yaml")

        if not oas_file or not os.path.exists(oas_file):
            return BaseResponse(
                success=False,
                error="OAS file not found",
            )
        description = kwargs.get("description") or asset.get("description", "")
        tags = kwargs.get("tags") or asset.get(
            "tags", ["sf-api-catalog", "sf-api-topic"]
        )
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]
        implementation_uri = kwargs.get("implementation_uri") or api.get(
            "implementation_uri", public_url
        )
        if not implementation_uri:
            return BaseResponse(
                success=False,
                error="Implementation URI not found",
            )
        endpoint_uri = kwargs.get("endpoint_uri") or api.get("endpoint_uri")
        if not endpoint_uri:
            return BaseResponse(
                success=False,
                error="Endpoint URI not found",
            )
        endpoint_path = kwargs.get("endpoint_path") or api.get(
            "endpoint_path", name.replace("-", "_").lower()
        )
        if not endpoint_path:
            return BaseResponse(
                success=False,
                error="Endpoint path not found",
            )
        gateway_id = kwargs.get("gateway_id") or api.get("gateway_id")
        if not gateway_id:
            return BaseResponse(
                success=False,
                error="Gateway ID not found",
            )
        gateway_version = kwargs.get("gateway_version") or api.get("gateway_version")
        if not gateway_version:
            return BaseResponse(
                success=False,
                error="Gateway version not found",
            )
        ms_client = _get_mulesoft_client(profile_name)

        # if _get_mulesoft_client() failed, return the error
        if isinstance(ms_client, BaseResponse):
            return ms_client
        auth_check = ms_client._check_auth()
        if auth_check:
            return auth_check
        if not ms_client:
            return BaseResponse(
                success=False,
                error="Mulesoft client not found",
            )
        # publish the asset
        asset_result = ms_client.publish_exchange_asset(
            name=name,
            version=version,
            description=description,
            tags=tags,
            oas_file=oas_file,
        )
        if asset_result.get("status") not in ["success", "completed"]:
            return BaseResponse(
                success=False,
                error=f"Failed to publish asset: {asset_result.get('message')}",
            )

        ctx_mgr.update_platform(
            platform=ctx.get("active_platform"),
            environment=ctx.get("active_environment"),
            values={
                "mulesoft": {
                    "profile": profile_name,
                    "asset": {
                        "name": name,
                        "version": version,
                        "description": description,
                        "oas_file": oas_file,
                        "tags": tags,
                    },
                }
            },
        )

        # publish API
        api_result = ms_client.publish_api(
            name=name,
            version=version,
            implementation_uri=implementation_uri,
            endpoint_uri=endpoint_uri,
            endpoint_path=endpoint_path,
        )
        api_id = api_result.get("id")
        if not api_id:
            return BaseResponse(
                success=False,
                error=f"Failed to publish API: {api_result.get('message')}",
            )

        # deploy the API
        ms_client.deploy_api(
            api_id=api_id,
            gateway_id=gateway_id,
            gateway_version=gateway_version,
        )

        # update context
        ctx_mgr.update_platform(
            platform=ctx.get("active_platform"),
            environment=ctx.get("active_environment"),
            values={
                "mulesoft": {
                    "profile": profile_name,
                    "api": {
                        "api_id": api_id,
                        "gateway_id": gateway_id,
                        "gateway_version": gateway_version,
                        "endpoint_uri": endpoint_uri,
                        "endpoint_path": endpoint_path,
                    },
                }
            },
        )

        access_url = f"{endpoint_uri.rstrip('/')}/{endpoint_path.lstrip('/')}"

        return BaseResponse(
            success=True,
            app_name=app_name,
            api_id=api_id,
            access_url=access_url,
            message="API published successfully",
        )
