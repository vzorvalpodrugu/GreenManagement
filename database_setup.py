import asyncio
import os
import asyncpg
import logging
from dotenv import load_dotenv
from requests import sql_create_databases

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AsyncDataManagement:
    def __init__(
            self,
            username: str = os.getenv('db_username'),
            password: str = os.getenv('db_password'),
            port: str = os.getenv('db_port'),
            host: str = os.getenv('db_host'),
    ):
        self.username = username
        self.password = password
        self.port = port
        self.host = host


    async def create_database(self, db_name: str):
        try:
            conn = await asyncpg.connect(
                user=self.username,
                password=self.password,
                port=self.port,
                host=self.host,
                database='postgres'
            )

            try:
                exist = await conn.fetchval('SELECT * FROM pg_database WHERE datname = $1', db_name)

                if not exist:
                    await conn.execute(f'CREATE DATABASE {db_name}')
                    logger.info("Database has been created.")
                else:
                    logger.error("Database has been created early.")

            except Exception as e:
                logger.error(f'Error {e}')
        except Exception as e:
            logger.error(f'Database has not been created. Error {e}')

    async def create_tables(self, db_name: str):
        try:
            conn = await asyncpg.connect(
                user=self.username,
                password=self.password,
                port=self.port,
                host=self.host,
                database=db_name
            )

            try:
                async with conn.transaction():
                    await conn.execute(sql_create_databases)
                logger.info("Tables have been created.")
            except Exception as e:
                logger.error(f'Tables have not been created. Error: {e}')

        except Exception as e:
            logger.error(f'Error: {e}')

async def main():
    db_manager = AsyncDataManagement()
    await db_manager.create_database(os.getenv('db_name'))
    await db_manager.create_tables(os.getenv('db_name'))

if __name__ == "__main__":
    asyncio.run(main())