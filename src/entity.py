from datetime import datetime

from pydantic import BaseModel

class Entity(BaseModel):
    created_at: datetime | None = None  # auto-set by DB
    entity_id: int | None = None  # DB's row number
    name: str | None = None  # e.g., '@elvis' or 'pie'
    karma: int | None = None  # auto-set to default value by DB
    opted_in: bool | None = None  # auto-set to default value by DB
    user_id: str | None = None  # Slack's user ID
