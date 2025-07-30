"""
OpenAPI generation logic for AgentForce-enabled FastAPI applications.
"""

import inspect
from fastapi import FastAPI
from typing import Any, get_origin, get_args
from fastapi.openapi.utils import get_openapi

from sfai.core.agentforce.decorators import (
    AgentForceMetadata,
    AgentForceActionRouteMetadata,
)


def generate_agentforce_openapi(app: FastAPI) -> dict[str, Any]:
    """
    Generate OpenAPI schema with AgentForce extensions.

    Args:
        app: FastAPI application instance

    Returns:
        OpenAPI schema dictionary with AgentForce x-sfdc extensions
    """
    raw = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
        openapi_version=app.openapi_version,
    )

    # Remove 422 responses which are not needed
    for _, method_item in raw.get("paths", {}).items():
        for _, param in method_item.items():
            responses = param.get("responses", {})
            if "422" in responses:
                del responses["422"]

    schemas: dict[str, Any] = raw.get("components", {}).get("schemas", {})

    # Add AgentForce topic-level metadata
    (
        raw.setdefault("x-sfdc", {})
        .setdefault("agent", {})
        .setdefault("topic", {})
        .update(
            {
                "name": app.title,
                "classificationDescription": app.description,
                "scope": "Your job is to help test agentforce and mulesoft connection",
                "instructions": ["hi there"],
            }
        )
    )

    # Process routes for AgentForce metadata
    for route in app.routes:
        if not hasattr(route, "endpoint") or not getattr(
            route, "include_in_schema", False
        ):
            continue

        path = route.path
        for method in route.methods - {"HEAD", "OPTIONS"}:
            op_name = method.lower()
            if path not in raw["paths"] or op_name not in raw["paths"][path]:
                continue

            op = raw["paths"][path][op_name]
            fn = route.endpoint

            # 1) Operation-level metadata
            meta_op: AgentForceActionRouteMetadata | None = getattr(
                fn, AgentForceActionRouteMetadata.ATTRIBUTE_NAME, None
            )
            if meta_op:
                op["x-sfdc"] = {
                    "agent": {"action": meta_op.model_dump(exclude_none=True)}
                }

            # 2) Inline all $ref in requestBody & responses
            if "requestBody" in op:
                op["requestBody"] = _remove_inline_refs(op["requestBody"], schemas)
            for resp in op.get("responses", {}).values():
                if "content" in resp:
                    for media in resp["content"].values():
                        if "schema" in media:
                            media["schema"] = _remove_inline_refs(
                                media["schema"], schemas
                            )

            # 3) Parameter-level metadata → requestBody.schema.x-sfdc
            sig = inspect.signature(fn)

            # Find body-param metadata
            for param in sig.parameters.values():
                possible_parameter = [
                    p for p in op.get("parameters", []) if p["name"] == param.name
                ]
                if not possible_parameter:
                    # This must be a request body object
                    ann = param.annotation
                    if get_origin(ann) is not None:  # Handle Annotated types
                        base, *extras = get_args(ann)
                        for ex in extras:
                            if isinstance(ex, AgentForceMetadata):
                                if "requestBody" in op:
                                    op["requestBody"]["description"] = ex.description
                                    schema = op["requestBody"]["content"][
                                        "application/json"
                                    ]["schema"]
                                    schema["additionalProperties"] = False
                                    action: dict[str, bool] = {}
                                    if ex.is_user_input is not None:
                                        action["isUserInput"] = ex.is_user_input
                                    if ex.is_displayable is not None:
                                        action["isDisplayable"] = ex.is_displayable
                                    if action:
                                        (
                                            schema.setdefault("x-sfdc", {})
                                            .setdefault("agent", {})
                                            .setdefault("action", {})
                                            .update(action)
                                        )
                else:
                    request_parameter = possible_parameter[0]
                    ann = param.annotation
                    if get_origin(ann) is not None:  # Handle Annotated types
                        base, *extras = get_args(ann)
                        for ex in extras:
                            if isinstance(ex, AgentForceMetadata):
                                schema = request_parameter["schema"]
                                schema["additionalProperties"] = False
                                request_parameter["description"] = ex.description
                                action: dict[str, bool] = {}
                                if ex.is_user_input is not None:
                                    action["isUserInput"] = ex.is_user_input
                                if ex.is_displayable is not None:
                                    action["isDisplayable"] = ex.is_displayable
                                if action:
                                    (
                                        schema.setdefault("x-sfdc", {})
                                        .setdefault("agent", {})
                                        .setdefault("action", {})
                                        .update(action)
                                    )

            # 4) Return-type metadata → responses…schema.x-sfdc
            ret = sig.return_annotation
            if get_origin(ret) is not None:  # Handle Annotated types
                _, *extras = get_args(ret)
                for ex in extras:
                    if isinstance(ex, AgentForceMetadata):
                        for resp in op["responses"].values():
                            if (
                                "content" in resp
                                and "application/json" in resp["content"]
                            ):
                                schema = resp["content"]["application/json"]["schema"]
                                schema["additionalProperties"] = False
                                action: dict[str, bool] = {}
                                if ex.is_user_input is not None:
                                    action["isUserInput"] = ex.is_user_input
                                if ex.is_displayable is not None:
                                    action["isDisplayable"] = ex.is_displayable
                                if action:
                                    (
                                        schema.setdefault("x-sfdc", {})
                                        .setdefault("agent", {})
                                        .setdefault("action", {})
                                        .update(action)
                                    )

    # Remove components section to inline everything
    raw.pop("components", None)
    return raw


def _remove_inline_refs(obj: Any, schemas: dict[str, Any]) -> Any:
    """
    Traverse the schema tree to remove schema references and inline them.
    """
    if isinstance(obj, dict):
        if "$ref" in obj:
            ref = obj["$ref"].split("/")[-1]
            return _remove_inline_refs(schemas[ref], schemas)
        return {k: _remove_inline_refs(v, schemas) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_remove_inline_refs(v, schemas) for v in obj]
    return obj
