from datetime import datetime

from pydantic import BaseModel

class Entity(BaseModel):
    created_at: datetime
    entities_table_id: int | None = None
    karma: int = 0
    name: str
    opted_in: bool = True
    user_id: str | None = None

    def add(self):
        entity_dao = EntityDAO()
        entity_dao.add_entity(self)