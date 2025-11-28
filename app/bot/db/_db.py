import sqlite3
import logging
from os import path, makedirs
from app.db._exceptions import CreateDBDirError

logger = logging.getLogger(__name__)
Conn = sqlite3.Connection
Cur = sqlite3.Cursor

class SQLiteDb:
    def __init__(self,
                 db_path: str) -> None:
        self._db_path: str = path.expanduser(db_path)
        self.__create_dbdir()
        self.__init_db()
    
    def __init_db(self) -> None:
        self._con: Conn = sqlite3.connect(self._db_path)
        self._cur: Cur = self._con.cursor()
        self.__create_default_tables()
        
        
    def __create_default_tables(self) -> None:
        self._cur.execute(
'''
CREATE TABLE IF NOT EXISTS dens (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name VARCHAR(50) NOT NULL,
    url TEXT NOT NULL,
    u_type VARCHAR(2) NOT NULL,
    last_checked DATETIME DEFAULT CURRENT_TIMESTAMP
)
'''
        )
        self._cur.execute(
'''
CREATE TABLE IF NOT EXISTS vacs (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    denid INT,
    name VARCHAR(100) NOT NULL,
    url TEXT NOT NULL,
    added DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(denid) REFERENCES dens(id) ON DELETE SET NULL
)
'''
        )
        self._con.commit()
        # datetimes in integer, as unix time the number of seconds since 1970-01-01
        # (ex: "VARCHAR(255)") are ignored by SQLite - SQLite does not impose any length restrictions
        # пишу просто для удобства
        # DATETIME -> NUMERIC -> INTEGER
        
    
    def __create_dbdir(self) -> None:
        if self.__is_memory_db():
            return
        dbdir, db_name = path.split(self._db_path)
        
        if not db_name.endswith('.db'):
            dbdir = path.join(dbdir, db_name)
            self._db_path = path.join(dbdir, 'sqlite.db')
        
        if not path.isdir(dbdir):
            try:
                makedirs(dbdir, mode=0o755, exist_ok=True)
                # 0o777 все права всем 0о755 - владелец всё, остальные чтение и выполнение
                # exist ok - не генерирует исключение если целевой каталог существует
            except OSError as ex:
                logger.critical(f'Failed to create {dbdir}: {ex}')
                raise CreateDBDirError()
    
    def __is_memory_db(self) -> bool:
        # means also file::memory:... but i don't understand a URI filename
        # без URI, это в целом отдельная функция и включается она в 
        # sqlite3.connect(..., uri=True)
        return ':memory:' in self._db_path