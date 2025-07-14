from pydantic import BaseModel, Field
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
    platform: Dict[str, PlatformContext] = Field(
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
