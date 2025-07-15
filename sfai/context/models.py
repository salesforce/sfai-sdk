from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class PlatformContext(BaseModel):
    class Config:
        extra = "allow"


class ApplicationContext(BaseModel):
    app_name: str = Field(..., min_length=1, description="The name of the application")
    active_platform: str = Field(
        ..., description="The active platform for the application"
    )
    active_environment: str = Field(
        default="default", description="The active environment for the application"
    )
    platform: Dict[str, Any] = Field(
        default_factory=dict, description="The platform context for the application"
    )
    integrations: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="The integrations for the application"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="The date and time the application context was created",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="The date and time the application context was last updated",
    )

    @field_validator("platform", mode="before")
    @classmethod
    def migrate_platform_format(cls, v):
        """
        Migrate old platform format to new environment-nested format.

        Old format: platform.heroku = {app_name: "x", git_url: "y"}
        New format: platform.heroku.default = {app_name: "x", git_url: "y"}
        """
        if not isinstance(v, dict):
            return v

        migrated = {}
        for platform_name, platform_data in v.items():
            if not isinstance(platform_data, dict):
                # Skip non-dict values
                migrated[platform_name] = platform_data
                continue

            # Check if this is already new format (has environment-like keys)
            # New format: all values should be dicts (environments)
            # Old format: values are mixed (strings, ints, dicts, etc.)

            has_environment_structure = all(
                isinstance(val, dict)
                for val in platform_data.values()
                if val is not None
            )

            if has_environment_structure and platform_data:
                # Already new format - keep as is
                migrated[platform_name] = platform_data
            else:
                # Old format - wrap in "default" environment
                migrated[platform_name] = {"default": platform_data}

        return migrated

    @field_validator("active_environment", mode="before")
    @classmethod
    def ensure_active_environment(cls, v):
        """Ensure active_environment defaults to 'default' for migrated contexts."""
        return v if v is not None else "default"

    class Config:
        extra = "allow"


class RegisteredApp(BaseModel):
    app_name: str = Field(..., min_length=1, description="The name of the application")
    path: str = Field(..., description="The path to the application")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="The date and time the application was registered",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="The date and time the application was last updated",
    )

    class Config:
        extra = "allow"


class GlobalContext(BaseModel):
    applications: List[RegisteredApp] = Field(
        default_factory=list, description="A list of registered applications"
    )
    service_profiles: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, description="A dictionary of service profiles"
    )

    class Config:
        extra = "allow"
