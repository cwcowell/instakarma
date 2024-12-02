from datetime import datetime

from pydantic import BaseModel

class Grant(BaseModel):
    amount: int
    granter_id: int
    recipient_id: int
    table_id: int | None = None
    timestamp: datetime
