from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

app = FastAPI()


@app.api_route(
    "/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
)
async def proxy(request: Request, path: str):
    return PlainTextResponse("Hello SFAI Users!")


@app.get("/health")
def health():
    return {"status": "healthy", "service": "sfai-app"}
