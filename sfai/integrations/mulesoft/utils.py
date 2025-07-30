from typing import Optional, Union
from sfai.context.manager import ContextManager
from sfai.integrations.mulesoft.core import MulesoftAPI
from rich.console import Console
from sfai.core.response_models import BaseResponse
from sfai.constants import ERROR_EMOJI, WARNING_EMOJI

console = Console()
ctx_mgr = ContextManager()


def _get_mulesoft_client(
    profile_name: Optional[str] = None,
) -> Union[Optional[MulesoftAPI], BaseResponse]:
    """
    Helper to create a MulesoftAPI client from context.

    Args:
        profile_name: Optional[str]
            Name of the MuleSoft profile for the environment

    Returns:
        Optional[MulesoftAPI]
            An authenticated client instance, or None if authentication fails
    """

    if not profile_name:
        context = ctx_mgr.read_context()
        if not context:
            console.print(f"{ERROR_EMOJI} No context found.")
            console.print(f"{WARNING_EMOJI} Run `sfai init` to create a new context.")
            return {"success": False, "message": "No context found"}
        mulesoft_config = context.get("mulesoft", {})
        profile_name = mulesoft_config.get("profile", "default")
        if not profile_name:
            console.print(f"{ERROR_EMOJI} No MuleSoft profile configured for this app.")
            console.print(
                f"{WARNING_EMOJI} Please either:\n"
                "1. Run `sfai mulesoft configure` to set up a profile for this app\n"
                "2. Use --profile option to specify a profile to use"
            )
            return {
                "success": False,
                "message": "No MuleSoft profile configured for this app",
            }

    mulesoft_config = ctx_mgr.get_service_profile("mulesoft", profile_name)
    if not mulesoft_config:
        console.print(f"{ERROR_EMOJI} Missing MuleSoft configuration.")
        console.print(
            f"{WARNING_EMOJI} Run `sfai connect mulesoft` to configure "
            f"MuleSoft credentials."
        )
        return {"success": False, "message": "Missing MuleSoft configuration"}

    # Only org_id and environment_id are required
    required_keys = ["org_id", "environment_id", "client_id", "client_secret"]
    missing_keys = [key for key in required_keys if not mulesoft_config.get(key)]

    if missing_keys:
        return BaseResponse(
            success=False,
            message=(
                f"Missing required fields for authenticating with MuleSoft: "
                f"{', '.join(missing_keys)}"
            ),
        )

    return MulesoftAPI(
        org_id=mulesoft_config["org_id"],
        environment_id=mulesoft_config["environment_id"],
        client_id=mulesoft_config["client_id"],
        client_secret=mulesoft_config["client_secret"],
    )
