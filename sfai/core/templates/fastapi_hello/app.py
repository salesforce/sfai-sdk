from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Annotated

# Import AgentForce decorators for MuleSoft integration
from sfai.core.agentforce import AgentForceMetadata, agentforce_action

app = FastAPI(
    title="SFAI Template",
    description="FastAPI app with AgentForce integration",
    version="1.0.0",
)


# Example request/response models
class InvocationRequest(BaseModel):
    account_id: str


class InvocationResponse(BaseModel):
    customerId: str
    prediction: str


@app.api_route(
    "/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
)
async def proxy(request: Request, path: str):
    return PlainTextResponse("Hello SFAI Users!")


@app.get("/health")
def health():
    return {"status": "healthy", "service": "sfai-app"}


@app.post("/invocation")
@agentforce_action(publish_as_agent_action=True)
def invoke(
    request: Annotated[
        InvocationRequest,
        AgentForceMetadata(is_user_input=True, description="request body description"),
    ],
) -> Annotated[
    InvocationResponse,
    AgentForceMetadata(is_displayable=True, description="Successful response"),
]:
    """
    Invoke endpoint

    Example endpoint showing AgentForce decorator and metadata usage.
    This will automatically generate proper OpenAPI spec for MuleSoft publishing.
    """
    return InvocationResponse(
        customerId=request.account_id, prediction="sample prediction"
    )
