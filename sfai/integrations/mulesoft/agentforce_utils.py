import os
import sys
import importlib.util
import yaml
from pathlib import Path

from sfai.core.response_models import BaseResponse
from sfai.core.agentforce.generator import custom_openapi
from rich.console import Console

console = Console()


def detect_agentforce_usage(app_file: str) -> bool:
    """
    Detect if a Python file uses AgentForce decorators.

    Args:
        app_file: Path to the Python application file

    Returns:
        True if AgentForce decorators are detected, False otherwise
    """
    if not os.path.exists(app_file):
        return False

    try:
        with open(app_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Quick string search first (fast check)
        agentforce_indicators = [
            "agentforce_action",
            "AgentForceMetadata",
            "sfai.core.agentforce",
        ]

        for indicator in agentforce_indicators:
            if indicator in content:
                return True

        return False

    except Exception as e:
        console.print(f"[yellow]Warning: Could not parse {app_file}: {e}[/]")
        return False


def generate_openapi_from_app(app_file: str = "app.py") -> BaseResponse:
    """
    Generate OpenAPI spec from a FastAPI app with AgentForce decorators.

    Args:
        app_file: Path to the FastAPI application file

    Returns:
        BaseResponse indicating success/failure and generated file path
    """
    if not os.path.exists(app_file):
        return BaseResponse(
            success=False, error=f"Application file {app_file} not found"
        )

    if not detect_agentforce_usage(app_file):
        return BaseResponse(
            success=False,
            error=(
                "No AgentForce decorators detected. Please use @agentforce_action "
                "decorators for MuleSoft publishing."
            ),
        )

    try:
        # Import the app module dynamically
        app_module = _import_app_module(app_file)
        if not app_module:
            return BaseResponse(
                success=False, error=f"Could not import FastAPI app from {app_file}"
            )

        # Get the FastAPI app instance
        app = getattr(app_module, "app", None)
        if not app:
            return BaseResponse(
                success=False, error="No 'app' FastAPI instance found in the module"
            )

        # Generate OpenAPI schema with AgentForce extensions
        openapi_schema = custom_openapi(app)

        # Save to openapi.yaml
        output_file = "openapi.yaml"
        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(openapi_schema, f, default_flow_style=False, sort_keys=False)

        console.print(f"[green]✓ Generated OpenAPI spec: {output_file}[/]")

        return BaseResponse(
            success=True,
            message=f"OpenAPI spec generated successfully: {output_file}",
            data={"openapi_file": output_file},
        )

    except Exception as e:
        return BaseResponse(
            success=False, error=f"Failed to generate OpenAPI spec: {e!s}"
        )


def _import_app_module(app_file: str):
    """
    Dynamically import a Python module from file path.

    Args:
        app_file: Path to the Python file

    Returns:
        Imported module or None if failed
    """
    try:
        # Add current directory to Python path
        app_dir = os.path.dirname(os.path.abspath(app_file))
        if app_dir not in sys.path:
            sys.path.insert(0, app_dir)

        # Import the module
        module_name = Path(app_file).stem
        spec = importlib.util.spec_from_file_location(module_name, app_file)
        if not spec or not spec.loader:
            return None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module

    except Exception as e:
        console.print(f"[red]Error importing {app_file}: {e}[/]")
        return None


def validate_generated_openapi(openapi_file: str) -> BaseResponse:
    """
    Validate that the generated OpenAPI file has required AgentForce extensions.

    Args:
        openapi_file: Path to the OpenAPI YAML file

    Returns:
        BaseResponse indicating validation result
    """
    if not os.path.exists(openapi_file):
        return BaseResponse(
            success=False, error=f"OpenAPI file {openapi_file} not found"
        )

    try:
        with open(openapi_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Check for required AgentForce extensions
        if "x-sfdc" not in data:
            return BaseResponse(
                success=False, error="Missing x-sfdc extension in OpenAPI spec"
            )

        agent_data = data.get("x-sfdc", {}).get("agent", {})
        if "topic" not in agent_data:
            return BaseResponse(
                success=False, error="Missing x-sfdc.agent.topic in OpenAPI spec"
            )

        # Check for at least one endpoint with AgentForce action
        paths = data.get("paths", {})
        has_agentforce_action = False

        for path, methods in paths.items():
            for method, spec in methods.items():
                if isinstance(spec, dict) and "x-sfdc" in spec:
                    agent_action = (
                        spec.get("x-sfdc", {}).get("agent", {}).get("action", {})
                    )
                    if agent_action.get("publishAsAgentAction"):
                        has_agentforce_action = True
                        break
            if has_agentforce_action:
                break

        if not has_agentforce_action:
            return BaseResponse(
                success=False,
                error="No endpoints with publishAsAgentAction found in OpenAPI spec",
            )

        return BaseResponse(success=True, message="OpenAPI spec validation passed")

    except Exception as e:
        return BaseResponse(
            success=False, error=f"Failed to validate OpenAPI spec: {e!s}"
        )
