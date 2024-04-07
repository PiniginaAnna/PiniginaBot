import sqlite3
from aiogram import Bot, Dispatcher
from dataclasses import dataclass
from config import token
from aiogram.contrib.fsm_storage.memory import MemoryStorage


@dataclass
class Database:
    """Создание базы данных для бота и работа с ней"""
    db_name: str
    connection: sqlite3.Connection = None
    cursor: sqlite3.Cursor = None

    def __post_init__(self):
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def create_users_table(self):
        with self.connection:
            self.cursor.execute(f'create table users (id integer, user_name varchar(45), user_date date)')

    def insert_user(self, id, user_name, user_date):
        with self.connection:
            self.cursor.execute(f'insert into users (id, user_name, user_date) values ({id}, "{user_name}", "{user_date}")')

    def select_user(self, id):
        with self.connection:
            self.cursor.execute(f'select user_name from users where id={id}')
            user_name = self.cursor.fetchone()
            return user_name[0]

    def create_pictures_table(self):
        with self.connection:
            self.cursor.execute(f'create table pictures (smiles text, picture text)')

    def insert_picture(self, smiles, picture):
        with self.connection:
            self.cursor.execute(f'insert into pictures (smiles, picture) values ("{smiles}", "{picture}")')


class PiniginaBot(Bot):
    """Создает мой бот"""
    def __init__(self, token, database):
        super().__init__(token=token)
        self.database = database


bot = PiniginaBot(token, Database('/mnt/d/projects/bot_databases/pinigina_bot.sqlite'))
memory_storage = MemoryStorage()
dispatcher = Dispatcher(bot, storage=memory_storage)


if __name__ == '__main__':
    database = Database('/mnt/d/projects/bot_databases/pinigina_bot.sqlite')

    database.create_users_table()
    database.insert_user(1, 'Anna', '1998-05-14')

    database.create_pictures_table()
    database.insert_picture('test', '111111')
