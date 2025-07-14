import shutil
from pathlib import Path
from sfai.context.manager import ContextManager
from sfai.core.response_models import BaseResponse
from sfai.constants import CHARTS_PATH, WARNING_EMOJI, WARNING_COLOR
from rich.console import Console

console = Console()


def download_helm_chart() -> BaseResponse:
    try:
        ctx_mgr = ContextManager()
        context = ctx_mgr.read_context()
        if not context:
            return BaseResponse(
                success=False,
                app_name=None,
                error="No app context found",
            )
        chart_path = CHARTS_PATH
        if not chart_path.exists():
            return BaseResponse(
                success=False,
                error="Helm chart not found",
            )

        # Download the chart
        destination_path = Path("./helm-chart")
        if destination_path.exists():
            shutil.rmtree(destination_path)
        shutil.copytree(chart_path, destination_path)

        # Show warning about local chart usage
        console.print(
            f"{WARNING_EMOJI} [{WARNING_COLOR}]Custom helm chart found. This "
            f"chart folder will be used for future deployments. Delete "
            f"./helm-chart to use the default chart.[/]"
        )

        return BaseResponse(
            success=True,
            message="Helm chart downloaded successfully",
            app_name=context.get("app_name"),
            platform=context.get("platform"),
        )
    except ValueError as e:
        return BaseResponse(success=False, error=f"Context validation error: {e!s}")
