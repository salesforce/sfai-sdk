from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

# Import AgentForce decorators for MuleSoft integration
from sfai.core.agentforce import agentforce_action

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


@app.get("/")
async def root():
    return PlainTextResponse("Hello SFAI Users!")


@app.get("/{path:path}")
async def catch_all_get(path: str):
    return PlainTextResponse("Hello SFAI Users!")


@app.get("/health")
def health():
    return {"status": "healthy", "service": "sfai-app"}


@app.post("/invocation")
@agentforce_action(publish_as_agent_action=True)
def invoke(request: InvocationRequest) -> InvocationResponse:
    """
    Invoke endpoint

    This endpoint will be published to MuleSoft/AgentForce.
    """
    return InvocationResponse(
        customerId=request.account_id, prediction="sample prediction"
    )
