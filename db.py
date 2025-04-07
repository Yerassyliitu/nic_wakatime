import asyncpg

db_pool: asyncpg.Pool = None


async def init_db_pool(database_url: str):
    global db_pool
    db_pool = await asyncpg.create_pool(database_url)
    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                telegram_id BIGINT PRIMARY KEY,
                username TEXT,
                wakatime_key TEXT
            )
        """
        )


async def save_contact(username: str, telegram_id: int):
    """
    Сохраняет или обновляет username пользователя.
    """
    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO users (telegram_id, username)
            VALUES ($1, $2)
            ON CONFLICT (telegram_id) DO UPDATE
              SET username = EXCLUDED.username
        """,
            telegram_id,
            username,
        )


async def save_wakatime_key(telegram_id: int, waka_key: str):
    """
    Сохраняет или обновляет WakaTime API ключ для пользователя.
    """
    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO users (telegram_id, wakatime_key)
            VALUES ($1, $2)
            ON CONFLICT (telegram_id) DO UPDATE
              SET wakatime_key = EXCLUDED.wakatime_key
        """,
            telegram_id,
            waka_key,
        )


async def get_all_users():
    """
    Возвращает список кортежей (telegram_id, username, wakatime_key) для всех пользователей.
    """
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT telegram_id, username, wakatime_key FROM users")
    return [(row["telegram_id"], row["username"], row["wakatime_key"]) for row in rows]
