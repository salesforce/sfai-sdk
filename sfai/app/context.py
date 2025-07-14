from sfai.context.manager import ContextManager
from sfai.constants import CONTEXT_FILE
from sfai.core.response_models import BaseResponse

ctx_mgr = ContextManager()


def get_context() -> BaseResponse:
    try:
        context = ctx_mgr.read_context()
        if not context:
            return BaseResponse(
                success=False,
                app_name=None,
                error="No app context found",
            )
        return BaseResponse(
            success=True,
            app_name=context.get("app_name"),
            platform=context.get("active_platform"),
            context=context,
        )
    except ValueError as e:
        return BaseResponse(
            success=False,
            app_name=None,
            error=str(e),
        )


def delete_context() -> BaseResponse:
    """
    Delete the current context
    """
    try:
        context = ctx_mgr.read_context()
        if not context:
            return BaseResponse(
                success=False,
                app_name=None,
                error="No app context found",
            )
        app_name = context.get("app_name")
        if CONTEXT_FILE.exists():
            CONTEXT_FILE.unlink()
            ctx_mgr.unregister_app(app_name)
            return BaseResponse(
                success=True,
                app_name=app_name,
                message=f"Context for {app_name} deleted and unregistered",
            )
        else:
            return BaseResponse(
                success=False,
                app_name=app_name,
                error=f"Context for {app_name} not found",
            )
    except ValueError as e:
        return BaseResponse(
            success=False,
            app_name=app_name,
            error=str(e),
        )
