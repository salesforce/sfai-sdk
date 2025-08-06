from typing import Any


def ensure_descriptions(schema: dict[str, Any]):
    props = schema.get("properties", {})
    for name, field in props.items():
        # Skip if description is already present
        if "description" not in field or not field["description"].strip():
            # generate a sentence-like fallback
            clean_name = name.replace("_", " ").capitalize()
            field["description"] = f"{clean_name} of the action"
