from typing import Tuple, List

import aiosqlite

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
                                'tg_id INTEGER NOT NULL UNIQUE)')

        await self.conn.execute('CREATE TABLE IF NOT EXISTS catalogs('
                                'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                                'name TEXT DEFAULT "Без названия",'
                                'user_tg_id INTEGER NOT NULL,'
                                'FOREIGN KEY (user_tg_id) REFERENCES users(tg_id) ON DELETE CASCADE)')

        await self.conn.execute('CREATE TABLE IF NOT EXISTS tasks('
                                'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                                'name TEXT NOT NULL ,'
                                'description TEXT,'
                                'deadline INTEGER,'
                                'created_at INTEGER,'
                                'catalog_id INTEGER NOT NULL,'
                                'FOREIGN KEY (catalog_id) REFERENCES catalogs(id) ON DELETE CASCADE)')

        await self.conn.commit()

    async def add_user(self, user_tg_id: int, username: str) -> None:
        user = await self.get_user_by_tg_id(user_tg_id)
        if not user:
            await self.conn.execute('INSERT INTO users (tg_id, username) VALUES (?, ?)', (user_tg_id, username))
        await self.conn.commit()

    async def create_catalog(self, user_tg_id: int, catalog_name: str) -> int:
        cursor = await self.conn.execute('INSERT INTO catalogs (name, user_tg_id) VALUES (?, ?)', (catalog_name, user_tg_id,))
        await self.conn.commit()
        return cursor.lastrowid


    async def create_task(self, catalog_id: int, task_name: str) -> int:
        cursor = await self.conn.execute('INSERT INTO tasks (name, catalog_id) VALUES (?, ?)', (task_name, catalog_id,))
        await self.conn.commit()
        return cursor.lastrowid


    async def get_user_by_tg_id(self, user_tg_id: int) -> Tuple:
        cursor = await self.conn.execute('SELECT * FROM users WHERE tg_id = ?', (user_tg_id,))
        user = await cursor.fetchone()
        return user

    async def get_catalog_names(self, user_tg_id: int) -> List[Tuple]:
        cursor = await self.conn.execute('SELECT name FROM catalogs WHERE user_tg_id = ?', (user_tg_id,))
        catalogs_names = await cursor.fetchall()
        return catalogs_names

    async def get_tasks(self, user_tg_id: int, catalog_name: str) -> List[Tuple]:
        cursor = await self.conn.execute('SELECT id FROM catalogs WHERE (user_tg_id, name) = (?, ?)',
                                         (user_tg_id, catalog_name))
        catalog_id = await cursor.fetchone()
        cursor = await self.conn.execute('SELECT name FROM tasks WHERE catalog_id = ?', (int(catalog_id[0]),))
        task_names = await cursor.fetchall()
        return task_names




def get_db() -> Database:
    """ Создает экземпляр базы данных.
    Глобальная переменная для обеспечения единственного экземпляра независимо от
    количества модулей, где используется данная функция """
    global db_instance
    if db_instance is None:
        db_instance = Database('tg_bd')
    return db_instance
