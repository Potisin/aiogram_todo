from typing import Tuple

import aiosqlite
from aiosqlite import Cursor

db_instance = None


class Database:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.conn = None

    async def connect(self) -> None:
        self.conn = await aiosqlite.connect(self.db_name)
        await self.conn.execute('PRAGMA foreign_keys = ON')

    async def close(self) -> None:
        if self.conn:
            await self.conn.close()

    async def create_tables(self) -> None:
        await self.conn.execute('CREATE TABLE IF NOT EXISTS users('
                                'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                                'username TEXT NOT NULL,'
                                'tg_id INTEGER NOT NULL)')

        await self.conn.execute('CREATE TABLE IF NOT EXISTS lists('
                                'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                                'name TEXT DEFAULT "Без названия",'
                                'user_id INTEGER NOT NULL,'
                                'FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)')

        await self.conn.execute('CREATE TABLE IF NOT EXISTS tasks('
                                'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                                'name TEXT NOT NULL ,'
                                'list_id INTEGER NOT NULL,'
                                'FOREIGN KEY (list_id) REFERENCES lists(id) ON DELETE CASCADE)')

        await self.conn.commit()

    async def add_user(self, user_tg_id: int, username: str) -> None:
        user = await self.get_user_by_tg_id(user_tg_id)
        if not user:
            await self.conn.execute('INSERT INTO users (tg_id, username) VALUES (?, ?)', (user_tg_id, username))
        await self.conn.commit()

    async def create_list(self, user_tg_id: int, list_name: str) -> None:
        await self.conn.execute('SELECT * FROM users WHERE tg_id = ?', (user_tg_id,))
        user = await self.get_user_by_tg_id(user_tg_id)
        user_id = user[0]
        await self.conn.execute('INSERT INTO lists (name, user_id) VALUES (?, ?)', (list_name, user_id,))
        await self.conn.commit()

    async def get_user_by_tg_id(self, user_tg_id: int) -> Tuple:
        cursor = await self.conn.execute('SELECT * FROM users WHERE tg_id = ?', (user_tg_id,))
        user = await cursor.fetchone()
        return user


def get_db() -> Database:
    """ Создает экземпляр базы данных.
    Глобальная переменная для обеспечения единственного экземпляра независимо от
    количества модулей, где используется данная функция """
    global db_instance
    if db_instance is None:
        db_instance = Database('tg_bd')
    return db_instance
