import logging

import asyncpg
from datetime import datetime
from typing import List, Optional
import os
import dotenv
from dotenv import load_dotenv
from datetime import datetime

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

    async def get_balance(self):
        async with self.pool.acquire() as conn:
            balance = await conn.fetch('SELECT * FROM balance;')

            return float(balance[0]['amount'])

    async def set_balance(self, balance):
        async with self.pool.acquire() as conn:
            balance = await conn.fetch(f"""
            UPDATE balance 
            SET amount = {balance};
            """)


    async def show_incomes(self, period: str) -> str:
        """Стильный отчет о доходах с зелеными плюсами"""
        async with self.pool.acquire() as conn:
            # Определяем запрос в зависимости от периода
            if period == 'Сегодня':
                records = await conn.fetch("""
                    SELECT amount, created_at FROM incomes 
                    WHERE DATE(created_at) = CURRENT_DATE 
                    ORDER BY created_at DESC;
                """)
            elif period == 'Вчера':
                records = await conn.fetch("""
                    SELECT amount, created_at FROM incomes 
                    WHERE DATE(created_at) = CURRENT_DATE - INTERVAL '1 day'
                    ORDER BY created_at DESC;
                """)
            elif period == 'Неделя':
                records = await conn.fetch("""
                    SELECT amount, created_at FROM incomes 
                    WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
                    ORDER BY created_at DESC;
                """)
            elif period == 'Месяц':
                records = await conn.fetch("""
                    SELECT amount, created_at FROM incomes 
                    WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
                    ORDER BY created_at DESC;
                """)
            else:
                records = []

        # Форматируем результат
        if not records:
            return f"📭 Нет доходов за {period.lower()}"

        # Считаем общую сумму
        total_amount = sum(float(record['amount']) for record in records)

        # Форматируем сумму с разделителями тысяч
        formatted_total = f"{total_amount:,.2f}".replace(',', ' ')

        # Начинаем формировать сообщение
        lines = [

        ]

        # Добавляем записи
        for record in records:
            amount = float(record['amount'])
            created_at = record['created_at']

            # Форматируем дату
            if period in ['Сегодня', 'Вчера']:
                # Для сегодня/вчера показываем время и день недели
                date_str = created_at.strftime("%H:%M")
            else:
                # Для недели/месяца показываем дату
                date_str = created_at.strftime("%d.%m %H:%M")

            # Форматируем сумму
            formatted_amount = f"{amount:,.2f}".replace(',', ' ')

            lines.append(f"🟢 +{formatted_amount} руб ({date_str})")

        # Добавляем итог
        lines.append("")
        lines.append(f"💎 <b>Всего:</b> {formatted_total} руб")

        # Если записей много, показываем количество
        if len(records) > 6:
            lines.insert(4, f"<i>Показано 6 из {len(records)} записей</i>")
            lines.append(f"<i>... и ещё {len(records) - 6} записей</i>")

        return "\n".join(lines)

    async def show_costs(self, period: str) -> str:
        """Отчет о расходах с динамическим итоговым смайликом"""
        async with self.pool.acquire() as conn:
            conditions = {
                'Сегодня': "DATE(created_at) = CURRENT_DATE",
                'Вчера': "DATE(created_at) = CURRENT_DATE - INTERVAL '1 day'",
                'Неделя': "created_at >= CURRENT_DATE - INTERVAL '7 days'",
                'Месяц': "created_at >= CURRENT_DATE - INTERVAL '30 days'"
            }

            condition = conditions.get(period, conditions['Сегодня'])
            records = await conn.fetch(f"""
                SELECT amount, category, created_at 
                FROM costs 
                WHERE {condition}
                ORDER BY created_at DESC;
            """)

        if not records:
            return f"📭 Нет расходов за {period.lower()}"

        total = sum(float(r['amount']) for r in records)
        formatted_total = f"{total:,.2f}".replace(',', ' ')

        # Эмодзи для категорий
        emojis = {
            'Еда': '🍔', 'Транспорт': '🚗', 'Одежда': '👕',
            'Развлечения': '🎮', 'Здоровье': '💊', 'Прочее': '💡',
            'Жилье': '🏠', 'Связь': '📱', 'Образование': '📚'
        }

        lines = [

        ]

        for record in records:
            amount = float(record['amount'])
            category = record['category']
            time = record['created_at']

            # Форматируем время
            if period in ['Сегодня', 'Вчера']:
                time_str = time.strftime("%H:%M")
            else:
                time_str = time.strftime("%d.%m %H:%M")

            emoji = emojis.get(category, '📌')
            formatted_amount = f"{amount:,.2f}".replace(',', ' ')
            lines.append(f"💸{formatted_amount} руб ({category} {emoji} {time_str})")

        lines.append("")

        total_emoji = "💰"

        lines.append(f"{total_emoji} Всего расходов: {formatted_total} руб")

        return "\n".join(lines)

db = Database()

