from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic import ValidationError

from sfai.constants import CONTEXT_FILE, CONTEXT_DIR, GLOBAL_APPS_FILE
from sfai.core.response_models import BaseResponse
from sfai.constants import SUCCESS_EMOJI, ERROR_EMOJI
from sfai.context.models import (
    ApplicationContext,
    GlobalContext,
    RegisteredApp,
    PlatformContext,
)


class ContextManager:
    def __init__(self):
        """
        Initialize the ContextManager.

        Args:
            None

        Returns:
            None
        """
        self.context_file = CONTEXT_FILE
        self.context_dir = CONTEXT_DIR
        self.global_context_file = GLOBAL_APPS_FILE

    def _load_json(self, file: Path) -> Dict[str, Any]:
        """
        Load JSON data from a file.

        Args:
            file: Path
                Path to the JSON file

        Returns:
            Dict[str, Any]
                The loaded JSON data as a dictionary
        """
        return json.loads(file.read_text()) if file.exists() else {}

    def _save_json(self, file: Path, data: Dict[str, Any]) -> None:
        """
        Save dictionary data to a JSON file.

        Args:
            file: Path
                Path to the JSON file
            data: Dict[str, Any]
                The data to save

        Returns:
            None
        """
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(json.dumps(data, indent=2, default=str))

    @staticmethod
    def _deep_merge(target: Dict[str, Any], source: Dict[str, Any]) -> None:
        for key, value in source.items():
            if isinstance(value, dict) and isinstance(target.get(key), dict):
                ContextManager._deep_merge(target[key], value)
            else:
                target[key] = value

    def read_context(
        self, platform: Optional[str] = None, environment: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Read application context from the context file.

        Args:
            platform: Optional[str]
                Platform name to read, uses active platform if None.
                Use this to get platform-specific data.
            environment: Optional[str]
                Environment name to read, uses active environment if None.
                Use this to get environment-specific data.

        Returns:
            Optional[Dict[str, Any]]
                The context data containing app_name, active_platform, and
                platform-specific data, or None if no context exists
        """
        try:
            data = self._load_json(self.context_file)
            if not data:
                return None

            context = ApplicationContext(**data)

            # get platform data from context
            platform = platform or context.active_platform
            environment = environment or context.active_environment
            if platform not in context.platform:
                return None
            platform_environments = context.platform.get(platform, {})
            if environment not in platform_environments:
                return None

            # Get the environment-specific data
            environment_data = platform_environments.get(environment, {})
            if isinstance(environment_data, PlatformContext):
                environment_data = environment_data.dict()

            result = {
                "app_name": context.app_name,
                "active_platform": platform,
                "active_environment": environment,
                **environment_data,
            }

            if context.integrations:
                result["integrations"] = context.integrations

            return result
        except ValidationError as e:
            raise ValueError(f"{ERROR_EMOJI} Invalid context data: {e}") from e

    def update_platform(
        self,
        platform: str,
        values: Dict[str, Any],
        environment: str = "default",
        app_name: Optional[str] = None,
    ) -> None:
        """
        Update platform values in the context.

        Args:
            platform: str
                Platform name to update
            values: Dict[str, Any]
                Values to set for the platform
            environment: str
                Environment name to update
            app_name: Optional[str]
                App name to update

        Returns:
            None
        """
        try:
            data = self._load_json(self.context_file)

            # update app name if provided
            if app_name:
                data["app_name"] = app_name

            # Ensure platform dictionaries exist
            if "platform" not in data:
                data["platform"] = {}
            if platform not in data["platform"]:
                data["platform"][platform] = {}
            if environment not in data["platform"][platform]:
                data["platform"][platform][environment] = {}

            self._deep_merge(data["platform"][platform][environment], values)
            data["active_platform"] = platform
            data["active_environment"] = environment

            context = ApplicationContext(**data)

            # save the updated context
            self._save_json(self.context_file, context.dict())
        except ValidationError as e:
            raise ValueError(f"{ERROR_EMOJI} Invalid context data: {e}") from e

    def clear_platform_keys(
        self, platform: str, environment: str = "default", keys: List[str] = []
    ) -> None:
        """
        Clear specific keys from the given platform block in the context.

        Args:
            platform: str
                The platform name (e.g., "heroku")
            keys: List[str]
                Keys to remove from that platform block
            environment: str
                Environment name to clear
        """
        try:
            data = self._load_json(self.context_file)
            if (
                "platform" not in data
                or platform not in data["platform"]
                or environment not in data["platform"][platform]
            ):
                return

            for key in keys:
                data["platform"][platform][environment].pop(key, None)

            context = ApplicationContext(**data)
            self._save_json(self.context_file, context.dict())
        except ValidationError as e:
            raise ValueError(f"{ERROR_EMOJI} Invalid context data: {e}") from e

    def register_app(self, app_name: str, path: str, **kwargs) -> None:
        """
        Register an app in the global registry.

        Args:
            app_name: str
                Name of the application
            path: str
                Path to the application directory
            **kwargs
                Additional context values to save

        Returns:
            None
        """
        try:
            data = self._load_json(self.global_context_file)
            abs_path = str(Path(path).resolve())

            # check if app already exists
            existing_apps = data.get("applications", [])
            if not any(app["path"] == abs_path for app in existing_apps):
                new_app = RegisteredApp(
                    app_name=app_name,
                    path=abs_path,
                    **kwargs,
                )

                if "applications" not in data:
                    data["applications"] = []
                data["applications"].append(new_app.dict())

                global_context = GlobalContext(**data)
                self._save_json(self.global_context_file, global_context.dict())
        except ValidationError as e:
            raise ValueError(f"{ERROR_EMOJI} Invalid app registration data: {e}") from e

    def unregister_app(self, app_name: str) -> BaseResponse:
        """
        Unregister an app from the global registry.

        Args:
            app_name: str
                Name of the application to unregister

        Returns:
            BaseResponse
                Response indicating success or failure
        """
        try:
            data = self._load_json(self.global_context_file)
            original = len(data.get("applications", []))
            data["applications"] = [
                app
                for app in data.get("applications", [])
                if app["app_name"] != app_name
            ]
            if len(data["applications"]) < original:
                global_context = GlobalContext(**data)
                self._save_json(self.global_context_file, global_context.dict())
                return BaseResponse(
                    success=True,
                    message=f"{SUCCESS_EMOJI} App '{app_name}' unregistered",
                )
            else:
                return BaseResponse(
                    success=False, error=f"{ERROR_EMOJI} App '{app_name}' not found"
                )
        except ValidationError as e:
            return BaseResponse(
                success=False, error=f"{ERROR_EMOJI} Invalid app registration data: {e}"
            )

    def add_service_profile(
        self, service: str, profile_name: str, config: dict
    ) -> None:
        """
        Add a service profile to the global context.

        Args:
            service: str
                The name of the service
        """
        if not service.strip():
            raise ValueError(f"{ERROR_EMOJI} service name is required")
        if not profile_name.strip():
            raise ValueError(f"{ERROR_EMOJI} profile name is required")
        try:
            data = self._load_json(self.global_context_file)
            profiles = data.setdefault("service_profiles", {})
            profiles.setdefault(service, {})[profile_name] = config

            global_context = GlobalContext(**data)
            self._save_json(self.global_context_file, global_context.dict())
        except ValidationError as e:
            raise ValueError(f"{ERROR_EMOJI} Invalid service profile data: {e}") from e

    def update_service_profile(
        self, service: str, profile_name: str, updates: dict
    ) -> None:
        """
        Update a service profile in the global context.

        Args:
            service: str
                The name of the service
        """
        try:
            data = self._load_json(self.global_context_file)
            service_profiles = data.setdefault("service_profiles", {})
            profiles = service_profiles.setdefault(service, {})

            if profile_name not in profiles:
                raise ValueError(f"Profile '{profile_name}' not found for '{service}'")

            profiles[profile_name].update(updates)
            global_context = GlobalContext(**data)
            self._save_json(self.global_context_file, global_context.dict())
        except ValidationError as e:
            raise ValueError(f"{ERROR_EMOJI} Invalid service profile data: {e}") from e

    def get_service_profile(
        self, service: str, profile_name: str = "default"
    ) -> Optional[Dict[str, Any]]:
        """
        Get a service profile from the global context.

        Args:
            service: str
                The name of the service
        """
        try:
            data = self._load_json(self.global_context_file)
            global_context = GlobalContext(**data)
            return global_context.service_profiles.get(service, {}).get(profile_name)
        except ValidationError as e:
            raise ValueError(f"{ERROR_EMOJI} Invalid global context data: {e}") from e

    def list_service_profiles(self, service: str) -> List[str]:
        """
        List all service profiles for a given service.

        Args:
            service: str
                The name of the service

        Returns:
            List[str]
                A list of all service profiles for the given service
        """
        try:
            data = self._load_json(self.global_context_file)
            global_context = GlobalContext(**data)
            return list(global_context.service_profiles.get(service, {}).keys())
        except ValidationError as e:
            raise ValueError(f"{ERROR_EMOJI} Invalid global context data: {e}") from e

    def delete_service_profile(self, service: str, profile_name: str) -> None:
        """
        Delete a service profile from the global context.

        Args:
            service: str
                The name of the service
        """
        try:
            data = self._load_json(self.global_context_file)
            profiles = data.get("service_profiles", {}).get(service, {})
            if profile_name in profiles:
                del profiles[profile_name]
            global_context = GlobalContext(**data)
            self._save_json(self.global_context_file, global_context.dict())
        except ValidationError as e:
            raise ValueError(f"{ERROR_EMOJI} Invalid global context data: {e}") from e

    def check_platform_environment(
        self, platform: str, environment: str
    ) -> Dict[str, Any]:
        """
        Check if a platform environment combination exists and provide detailed status.

        Args:
            platform: str
                Platform name to check
            environment: str
                Environment name to check

        Returns:
            Dict[str, Any]
                Status information including exists, available_environments, etc.
        """
        try:
            data = self._load_json(self.context_file)
            if not data:
                return {
                    "exists": False,
                    "platform_exists": False,
                    "available_environments": [],
                    "error": "No app context found",
                }

            context = ApplicationContext(**data)

            # Check if platform exists
            if platform not in context.platform:
                return {
                    "exists": False,
                    "platform_exists": False,
                    "available_platforms": list(context.platform.keys()),
                    "available_environments": [],
                    "error": f"Platform '{platform}' not initialized",
                }

            # Platform exists, check environment
            platform_environments = context.platform.get(platform, {})
            available_envs = (
                list(platform_environments.keys())
                if isinstance(platform_environments, dict)
                else []
            )

            if environment not in platform_environments:
                return {
                    "exists": False,
                    "platform_exists": True,
                    "available_environments": available_envs,
                    "error": (
                        f"Environment '{environment}' not found for platform "
                        f"'{platform}'"
                    ),
                }

            return {
                "exists": True,
                "platform_exists": True,
                "available_environments": available_envs,
                "error": None,
            }
        except (ValidationError, KeyError) as e:
            return {
                "exists": False,
                "platform_exists": False,
                "available_environments": [],
                "error": f"Context validation error: {e}",
            }
