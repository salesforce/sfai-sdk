from pydantic import BaseModel, Field


class MuleSoftConfig(BaseModel):
    org_id: str = Field(..., description="MuleSoft Organization ID")
    environment_id: str = Field(..., description="MuleSoft Environment ID")
    client_id: str = Field(..., description="MuleSoft Client ID")
    client_secret: str = Field(..., description="MuleSoft Client Secret")
