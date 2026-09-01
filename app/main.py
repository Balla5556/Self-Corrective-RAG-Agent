from __future__ import annotations

from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, Request
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.core.config import Settings
from app.core.schemas import ChatRequest, GatewayError
from app.core.service import GatewayService


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings.from_env()
    app.state.settings = settings
    app.state.gateway = GatewayService(settings)
    yield


app = FastAPI(title="Sentinel Gateway", version="1.0.0", lifespan=lifespan)


@app.exception_handler(GatewayError)
async def gateway_error_handler(request: Request, error: GatewayError):
    request_id = getattr(request.state, "request_id", str(uuid4()))
    return JSONResponse(
        status_code=error.status_code,
        content={"error": {"code": error.code, "message": error.message, "request_id": request_id}},
    )


@app.middleware("http")
async def correlation_id(request: Request, call_next):
    request.state.request_id = request.headers.get("x-request-id", str(uuid4()))
    response = await call_next(request)
    response.headers["x-sentinel-request-id"] = request.state.request_id
    return response


def tenant_from_auth(authorization: str = Header(default="")) -> str:
    if not authorization.startswith("Bearer "):
        raise GatewayError(401, "unauthorized", "Bearer API key required.")
    api_key = authorization.removeprefix("Bearer ").strip()
    tenant = app.state.settings.api_keys.get(api_key)
    if not tenant:
        raise GatewayError(401, "unauthorized", "Invalid API key.")
    return tenant


@app.get("/healthz", tags=["operations"])
async def healthz():
    return {"status": "ok"}


@app.get("/readyz", tags=["operations"])
async def readyz():
    return {"status": "ready", "provider": type(app.state.gateway.provider).__name__}


@app.get("/metrics", tags=["operations"])
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/v1/chat/completions", tags=["chat"])
async def chat_completion(payload: ChatRequest, tenant: str = Depends(tenant_from_auth)):
    response, request_id, pii_count = await app.state.gateway.process(tenant, payload)
    return {
        "id": f"chatcmpl-{request_id}",
        "object": "chat.completion",
        "model": response.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": response.content},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": response.input_tokens,
            "completion_tokens": response.output_tokens,
            "total_tokens": response.input_tokens + response.output_tokens,
        },
        "sentinel": {
            "request_id": request_id,
            "tenant": tenant,
            "pii_redacted": pii_count > 0,
            "redaction_count": pii_count,
        },
    }
