import inspect
from fastapi import FastAPI
from typing import Annotated, Any, get_origin, get_args, Optional
from fastapi.openapi.utils import get_openapi

from sfai.core.agentforce.decorators import (
    AgentForceMetadata,
    AgentForceActionRouteMetadata,
)


def custom_openapi(app: FastAPI) -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema

    raw = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
        openapi_version=app.openapi_version,
    )

    # remove 422 response which are not generated
    for _, method_item in raw.get("paths").items():
        for _, param in method_item.items():
            responses = param.get("responses")
            # remove 422 response, also can remove other status code
            if "422" in responses:
                del responses["422"]

    schemas: dict[str, Any] = raw.get("components", {}).get("schemas", {})
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

            # 1) operation-level metadata
            meta_op: Optional[AgentForceActionRouteMetadata] = getattr(
                fn, AgentForceActionRouteMetadata.ATTRIBUTE_NAME, None
            )
            if meta_op:
                op["x-sfdc"] = {
                    "agent": {"action": meta_op.model_dump(exclude_none=True)}
                }

            # 2) inline all $ref in requestBody & responses
            if "requestBody" in op:
                op["requestBody"] = remove_inline_refs(op["requestBody"], schemas)
            for resp in op.get("responses", {}).values():
                if "content" in resp:
                    for media in resp["content"].values():
                        if "schema" in media:
                            media["schema"] = remove_inline_refs(
                                media["schema"], schemas
                            )

            # 3) parameter-level metadata → requestBody.schema.x-sfdc
            sig = inspect.signature(fn)

            # find body-param metadata
            for param in sig.parameters.values():
                possible_parameter = [
                    p for p in op.get("parameters", []) if p["name"] == param.name
                ]
                if not possible_parameter:
                    # then is must be a request body object
                    ann = param.annotation
                    if get_origin(ann) is Annotated:
                        base, *extras = get_args(ann)
                        for ex in extras:
                            if isinstance(ex, AgentForceMetadata):
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
                    if get_origin(ann) is Annotated:
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

            # 4) return-type metadata → responses…schema.x-sfdc
            ret = sig.return_annotation
            if get_origin(ret) is Annotated:
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

    raw.pop("components", None)
    app.openapi_schema = raw
    return raw


def remove_inline_refs(obj: Any, schemas: dict[str, Any]) -> Any:
    """Traverse the schema tree to remove schema references and past them
    wherever they are used.
    """
    if isinstance(obj, dict):
        if "$ref" in obj:
            ref = obj["$ref"].split("/")[-1]
            return remove_inline_refs(schemas[ref], schemas)
        return {k: remove_inline_refs(v, schemas) for k, v in obj.items()}
    if isinstance(obj, list):
        return [remove_inline_refs(v, schemas) for v in obj]
    return obj
