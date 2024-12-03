from datetime import datetime

from pydantic import BaseModel

class Entity(BaseModel):
    name: str | None = None
    user_id: str | None = None
    karma: int | None = None
    created_at: datetime | None = None
    opted_in: bool | None = None
    entities_table_id: int | None = None

    # def __init__(self,
    #              name: str,
    #              user_id: None = None,
    #              karma: int = 0,
    #              opted_in: bool | None = None,
    #              created_at: datetime = None):
    #     self.name = name
    #     self.user_id = user_id
    #     self.karma = karma
    #     self.opted_in = opted_in
    #     self.created_at = created_at

    # def add(self):
        # entity_dao = EntityDAO()
        # entity_dao.add_entity(self)