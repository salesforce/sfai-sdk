from pydantic import BaseModel, Extra
from typing import Optional
import json
from json import dumps


class BaseResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    platform: Optional[str] = None
    app_name: Optional[str] = None

    class Config:
        extra = Extra.allow

    def with_update(self, **fields):
        """
        Update the response with new fields.
        """
        return self.copy(update=fields)

    def _repr_json_(self):
        return self.dict(exclude_none=True)

    def _repr_html_(self):
        return f"<pre>{dumps(self.dict(exclude_none=True), indent=2)}</pre>"

    def __repr__(self):
        return json.dumps(self.dict(exclude_none=True), indent=2)
