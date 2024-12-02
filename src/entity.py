from datetime import datetime

from pydantic import BaseModel

class Entity(BaseModel):
    created: datetime
    karma: int = 0
    name: str
    opted_in: bool = True
    user_id: str | None = None
    table_id: int | None = None
