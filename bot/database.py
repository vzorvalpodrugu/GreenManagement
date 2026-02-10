import logging

import asyncpg
from datetime import datetime
from typing import List, Optional
import os
import dotenv
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(
            self,
            username: str = os.getenv('db_username'),
            password: str = os.getenv('db_password'),
            port: str = os.getenv('db_port'),
            host: str = os.getenv('db_host'),
            database: str = os.getenv('db_name'),
        ):
        self.username = username
        self.password = password
        self.port = port
        self.host = host
        self.database = database
        self.pool : Optional[asyncpg.Pool] = None

    async def init_connection(self, conn):
        """Инициализируем каждое соединение в пуле"""
        # 1. Устанавливаем UTF-8 кодировку
        await conn.execute("SET client_encoding TO 'UTF8'")

        # 2. Можно также настроить другие параметры
        await conn.execute("SET timezone = 'UTC'")

        # 3. Опционально: настраиваем codec для текста
        await conn.set_type_codec(
            'text',
            encoder=lambda x: x,
            decoder=lambda x: x,
            schema='pg_catalog',
            format='text'
        )

    async def create_pool(self):
        self.pool = await asyncpg.create_pool(
            user=self.username,
            password=self.password,
            port=self.port,
            host=self.host,
            database=self.database,
            init=self.init_connection
        )
    async def add_income(self, amount: float):
        async with self.pool.acquire() as conn:
            await conn.fetchval("INSERT INTO incomes (amount) VALUES ($1)", amount)

    async def add_cost(self, category: str, amount: float):
        async with self.pool.acquire() as conn:
            await conn.fetchval("INSERT INTO costs (category, amount) VALUES ($1, $2);", category, amount)
db = Database()

