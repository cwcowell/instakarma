from entity import Entity
from db_mgr import DbMgr


class EntityDAO:

    def __init__(self, db_mgr: DbMgr):
        self.db_mgr: DbMgr = db_mgr


    def list_opted_out(self) -> list[Entity]:
        sql: str = """
            SELECT name
            FROM entities
            WHERE opted_in = FALSE
            ORDER BY name;
            """
        results: list[tuple] = self.db_mgr.execute_statement(sql)
        entities: list[Entity] = []
        for result in results:
            name: str = result[0]
            entity: Entity = Entity(name=name)
            entities.append(entity)
        return entities
