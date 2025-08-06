import inspect
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Annotated, Any, Callable, ClassVar, get_origin, get_args, Optional
from sfai.core.agentforce.helper import ensure_descriptions

from fastapi.openapi.utils import get_openapi


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


def custom_openapi(app: FastAPI) -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema

    raw = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
        openapi_version="3.0.3",  # Force 3.0.3 for MuleSoft compatibility
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
                "name": app.title.lower().replace(" ", "_"),
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
            if "description" not in op or not op["description"].strip():
                op["description"] = op.get("summary", "No description provided")
            if len(op["description"]) < 10:
                op["description"] += " - extended"

            fn = route.endpoint

            # 1) operation-level metadata
            meta_op = getattr(fn, AgentForceActionRouteMetadata.ATTRIBUTE_NAME, None)
            if meta_op:
                action_meta = meta_op.model_dump(exclude_none=True)
                op["x-sfdc"] = {"agent": {"action": action_meta}}

            # 2) inline all $ref in requestBody & responses
            if meta_op and "requestBody" in op:
                op["requestBody"].setdefault(
                    "description", "Request payload for agent action"
                )
                schema = op["requestBody"]["content"]["application/json"]["schema"]
                schema = remove_inline_refs(schema, schemas)
                schema.pop("title", None)
                op["requestBody"]["content"]["application/json"]["schema"] = schema
                ensure_descriptions(schema)
                schema.setdefault("additionalProperties", False)
                action_block = (
                    schema.setdefault("x-sfdc", {})
                    .setdefault("agent", {})
                    .setdefault("action", {})
                )
                action_block.setdefault("isUserInput", True)
                action_block.setdefault("isDisplayable", True)
                op["requestBody"]["content"]["application/json"]["schema"] = schema

            # Ensure operation has a description
            if "description" not in op or not op["description"].strip():
                op["description"] = op.get("summary", "No description provided")
            if len(op["description"]) < 10:
                op["description"] += " - extended"

            for resp in op.get("responses", {}).values():
                if "content" not in resp:
                    resp["content"] = {
                        "application/json": {
                            "schema": {"type": "object", "additionalProperties": False}
                        }
                    }
                for media in resp["content"].values():
                    if "schema" in media:
                        schema = remove_inline_refs(media["schema"], schemas)
                        schema.pop("title", None)
                        ensure_descriptions(schema)
                        schema.setdefault("additionalProperties", False)

                        if meta_op:
                            action_block = (
                                schema.setdefault("x-sfdc", {})
                                .setdefault("agent", {})
                                .setdefault("action", {})
                            )
                            action_block.setdefault("isUserInput", True)
                            action_block.setdefault("isDisplayable", True)
                        media["schema"] = schema

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
                                ensure_descriptions(schema)
                                if "type" in schema and schema["type"] == "object":
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
