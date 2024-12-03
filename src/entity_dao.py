from entity import Entity
from enums import Status
from db_mgr import DbMgr
from string_mgr import StringMgr

from logging import Logger
import sqlite3


class EntityDAO:

    def __init__(self, db_mgr: DbMgr, logger: Logger):
        self.db_mgr = db_mgr
        self.logger = logger

    def add(self, entity: Entity) -> None:
        sql: str = """
                   INSERT OR IGNORE INTO entities (name, user_id)
                   VALUES (?, ?);
                   """
        params: tuple = (entity.name, entity.user_id)
        try:
            self.db_mgr.execute_statement(sql, params)
        except sqlite3.Error as e:
            self.logger.error(StringMgr.get_string(key_path='entity.error.could-not-add-entity',
                                                   name=entity.name,
                                                   user_id=entity.user_id,
                                                   e=e))
            raise


    def is_in_db(self, entity: Entity) -> bool:
        sql: str = """
                   SELECT name
                   FROM entities
                   WHERE name = ? or user_id = ?;
                   """
        params: tuple = (entity.name, entity.user_id)
        try:
            results: list[tuple] = self.db_mgr.execute_statement(sql, params)
        except sqlite3.Error as e:
            self.logger.error(StringMgr.get_string(key_path='entity.error.could-not-check-if-entity-exists',
                                                   name=entity.name,
                                                   user_id=entity.user_id,
                                                   e=e))
            raise
        return len(results) > 0

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

    def set_status(self, entity: Entity, new_status: Status) -> None:
        sql: str = f"""
                   UPDATE entities
                   SET opted_in = ?
                   WHERE name = ?;
                   """
        params: tuple = (new_status == Status.OPTED_IN, entity.name)
        try:
            self.db_mgr.execute_statement(sql, params)
            self.logger.info(StringMgr.get_string(key_path='entity.current-status',
                                                  name=entity.name,
                                                  status=new_status.value))
        except sqlite3.Error as e:
            self.logger.error(StringMgr.get_string(key_path='entity.error.could-not-set-status',
                                                   name=entity.name,
                                                   status=new_status.value,
                                                   e=e))
            raise
