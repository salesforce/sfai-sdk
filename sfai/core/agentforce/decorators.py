"""
AgentForce decorators and metadata classes for FastAPI applications.
"""

from pydantic import BaseModel
from typing import ClassVar, Callable, Optional


class AgentForceMetadata:
    """
    Use in Annotated[...] to mark a body or return schema:
      - is_user_input  → x-sfdc/agent/action/isUserInput
      - is_displayable → x-sfdc/agent/action/isDisplayable
    """

    def __init__(
        self,
        *,
        is_user_input: Optional[bool] = None,
        is_displayable: Optional[bool] = None,
        description: Optional[str] = None,
    ):
        self.is_user_input = is_user_input
        self.is_displayable = is_displayable
        self.description = description or "default description"


class AgentForceActionRouteMetadata(BaseModel):
    ATTRIBUTE_NAME: ClassVar[str] = "_agentforce_matadata"

    publishAsAgentAction: bool = True
    isPii: Optional[bool] = None


def agentforce_action(
    _fn: Optional[Callable] = None,
    *,
    publish_as_agent_action: bool = True,
    is_pii: Optional[bool] = None,
) -> Callable:
    """
    Use on each @app.<method> to set:
      - x-sfdc/agent/action/publishAsAgentAction
      - x-sfdc/agent/action/isPii  (optional)
    Supports both @AgentforceAction  and  @AgentforceAction(is_pii=True)
    """

    def decorator(fn: Callable) -> Callable:
        setattr(
            fn,
            AgentForceActionRouteMetadata.ATTRIBUTE_NAME,
            AgentForceActionRouteMetadata(
                publishAsAgentAction=publish_as_agent_action, isPii=is_pii
            ),
        )
        return fn

    # If used without args
    if callable(_fn):
        return decorator(_fn)
    return decorator
