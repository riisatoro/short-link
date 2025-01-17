import sqlite3


USER_SCHEMA = """
create table if not exists users (
    id integer primary key autoincrement,
    username text not null,
    email text not null,
    password text not null
);
"""

URL_SCHEMA = """
create table if not exists urls (
    id integer primary key autoincrement,
    user_id integer not null,
    full_url text not null,
    short_url text not null,
    visits integer default 0,
    count_visits boolean default false,
    single_use boolean default false,
    foreign key (user_id) references users(id)
);
"""


class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name, autocommit=True)
        self.cursor = self.conn.cursor()

        self.cursor.execute(USER_SCHEMA)
        self.cursor.execute(URL_SCHEMA)

    async def create_table(self, table_name, columns):
        columns = ', '.join(columns)
        query = f'CREATE TABLE IF NOT EXISTS {table_name} ({columns})'
        await self.execute(query)
    
    async def insert(self, table_name, columns, values):
        columns = ', '.join(columns)
        values = ', '.join([f"'{value}'" for value in values])
        query = f'INSERT INTO {table_name} ({columns}) VALUES ({values})'
        await self.execute(query)
    
    async def select(self, table_name, columns, condition=None, single=False):
        columns = ', '.join(columns)
        query = f'SELECT {columns} FROM {table_name}'
        if condition:
            query += f' WHERE {condition}'
        return await self.execute(query, fetchall=not single)
    
    async def update(self, table_name, columns, values, condition):
        columns = ', '.join([f'{column} = "{value}"' for column, value in zip(columns, values)])
        query = f'UPDATE {table_name} SET {columns} WHERE {condition}'
        await self.execute(query)
    
    async def delete(self, table_name, condition):
        query = f'DELETE FROM {table_name} WHERE {condition}'
        await self.execute(query)
    
    async def execute(self, query, fetchall=False):
        if fetchall:
            return self.cursor.execute(query).fetchall()
        return self.cursor.execute(query).fetchone()


database = Database('url_shortener.db')
